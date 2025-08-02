#!/usr/bin/env python3
"""
Enhanced Duplicate Detector with GUI
Detects duplicate rows, duplicate columns, or duplicate values within columns in CSV and Excel files.
"""

import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

import pandas as pd


class DuplicateDetectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Duplicate Detector")
        self.root.geometry("900x750")
        self.root.minsize(800, 650)

        # Variables
        self.input_files = []
        self.output_directory = tk.StringVar()
        self.detection_mode = tk.StringVar(value="row")  # Default to row detection

        self.create_widgets()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame, text="Enhanced Duplicate Detector", font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Detection Mode Section
        mode_frame = ttk.LabelFrame(main_frame, text="Detection Mode", padding="10")
        mode_frame.grid(
            row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20)
        )

        ttk.Radiobutton(
            mode_frame, text="Row Detection", variable=self.detection_mode, value="row"
        ).grid(row=0, column=0, sticky=tk.W, padx=(0, 20))

        ttk.Radiobutton(
            mode_frame,
            text="Column Detection (Identical Columns)",
            variable=self.detection_mode,
            value="column",
        ).grid(row=0, column=1, sticky=tk.W, padx=(0, 20))

        ttk.Radiobutton(
            mode_frame,
            text="Column Values Detection",
            variable=self.detection_mode,
            value="column_values",
        ).grid(row=0, column=2, sticky=tk.W)

        # Mode description
        self.mode_description = ttk.Label(
            mode_frame,
            text="Row Detection: Identifies duplicate rows in your data",
            font=("Arial", 9),
            foreground="gray",
            wraplength=800,
        )
        self.mode_description.grid(
            row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0)
        )

        # Bind radio button changes to update description
        self.detection_mode.trace("w", self.update_mode_description)

        # Input Files Section
        ttk.Label(main_frame, text="Input Files:", font=("Arial", 12, "bold")).grid(
            row=2, column=0, sticky=tk.W, pady=(0, 5)
        )

        # Files listbox with scrollbar
        files_frame = ttk.Frame(main_frame)
        files_frame.grid(
            row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10)
        )
        files_frame.columnconfigure(0, weight=1)

        self.files_listbox = tk.Listbox(files_frame, height=6, selectmode=tk.EXTENDED)
        files_scrollbar = ttk.Scrollbar(
            files_frame, orient=tk.VERTICAL, command=self.files_listbox.yview
        )
        self.files_listbox.configure(yscrollcommand=files_scrollbar.set)

        self.files_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        files_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # File buttons
        file_buttons_frame = ttk.Frame(main_frame)
        file_buttons_frame.grid(row=4, column=0, columnspan=3, pady=(0, 20))

        ttk.Button(file_buttons_frame, text="Add Files", command=self.add_files).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(
            file_buttons_frame, text="Add Directory", command=self.add_directory
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            file_buttons_frame, text="Remove Selected", command=self.remove_selected
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_buttons_frame, text="Clear All", command=self.clear_all).pack(
            side=tk.LEFT, padx=(5, 0)
        )

        # Output Directory Section
        ttk.Label(
            main_frame, text="Output Directory:", font=("Arial", 12, "bold")
        ).grid(row=5, column=0, sticky=tk.W, pady=(10, 5))

        output_frame = ttk.Frame(main_frame)
        output_frame.grid(
            row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20)
        )
        output_frame.columnconfigure(0, weight=1)

        self.output_entry = ttk.Entry(
            output_frame, textvariable=self.output_directory, width=50
        )
        self.output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

        ttk.Button(
            output_frame, text="Browse", command=self.browse_output_directory
        ).grid(row=0, column=1)

        # Process Button
        self.process_button = ttk.Button(
            main_frame,
            text="Start Duplicate Detection",
            command=self.start_processing,
            style="Accent.TButton",
        )
        self.process_button.grid(row=7, column=0, columnspan=3, pady=(0, 20))

        # Progress Bar
        self.progress = ttk.Progressbar(main_frame, mode="indeterminate")
        self.progress.grid(
            row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10)
        )

        # Status/Log Area
        ttk.Label(main_frame, text="Processing Log:", font=("Arial", 12, "bold")).grid(
            row=9, column=0, sticky=tk.W, pady=(10, 5)
        )

        self.log_text = scrolledtext.ScrolledText(main_frame, height=12, width=70)
        self.log_text.grid(
            row=10,
            column=0,
            columnspan=3,
            sticky=(tk.W, tk.E, tk.N, tk.S),
            pady=(0, 10),
        )

        # Configure grid weights for resizing
        main_frame.rowconfigure(10, weight=1)

    def update_mode_description(self, *args):
        """Update the mode description based on selected detection mode."""
        if self.detection_mode.get() == "row":
            description = "Row Detection: Identifies duplicate rows in your data"
        elif self.detection_mode.get() == "column":
            description = "Column Detection: Identifies columns that have identical data (entire columns are duplicates)"
        else:  # column_values
            description = "Column Values Detection: Identifies duplicate values within each individual column"

        self.mode_description.config(text=description)

    def add_files(self):
        """Add individual files to the processing list."""
        files = filedialog.askopenfilenames(
            title="Select Files",
            filetypes=[
                ("Supported files", "*.csv *.xlsx *.xls"),
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx *.xls"),
                ("All files", "*.*"),
            ],
        )

        for file in files:
            if file not in self.input_files:
                self.input_files.append(file)
                self.files_listbox.insert(tk.END, os.path.basename(file))

        self.log(f"Added {len(files)} file(s)")

    def add_directory(self):
        """Add all supported files from a directory."""
        directory = filedialog.askdirectory(title="Select Directory")
        if not directory:
            return

        supported_extensions = [".csv", ".xlsx", ".xls"]
        files_added = 0

        for file_path in Path(directory).iterdir():
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                full_path = str(file_path)
                if full_path not in self.input_files:
                    self.input_files.append(full_path)
                    self.files_listbox.insert(tk.END, file_path.name)
                    files_added += 1

        self.log(f"Added {files_added} file(s) from directory: {directory}")

    def remove_selected(self):
        """Remove selected files from the list."""
        selected_indices = self.files_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "Please select files to remove.")
            return

        # Remove in reverse order to maintain indices
        for index in reversed(selected_indices):
            self.files_listbox.delete(index)
            del self.input_files[index]

        self.log(f"Removed {len(selected_indices)} file(s)")

    def clear_all(self):
        """Clear all files from the list."""
        self.files_listbox.delete(0, tk.END)
        self.input_files.clear()
        self.log("Cleared all files")

    def browse_output_directory(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_directory.set(directory)

    def log(self, message):
        """Add message to the log."""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def validate_inputs(self):
        """Validate user inputs before processing."""
        if not self.input_files:
            messagebox.showerror("Error", "Please select at least one file to process.")
            return False

        if not self.output_directory.get():
            messagebox.showerror("Error", "Please select an output directory.")
            return False

        if not os.path.exists(self.output_directory.get()):
            messagebox.showerror("Error", "Output directory does not exist.")
            return False

        return True

    def detect_duplicate_columns(self, df):
        """Detect duplicate columns in the dataframe."""
        # Transpose the dataframe to treat columns as rows for duplicate detection
        df_transposed = df.T

        # Find duplicate columns (now rows in transposed df)
        duplicate_cols = df_transposed.duplicated(keep=False)

        # Get the names of duplicate columns
        duplicate_column_names = df_transposed[duplicate_cols].index.tolist()

        return duplicate_column_names, duplicate_cols

    def detect_duplicate_values_in_columns(self, df):
        """Detect duplicate values within each column."""
        column_duplicates = {}
        duplicate_info = {}

        for column in df.columns:
            # Get the series for this column
            col_series = df[column]

            # Find duplicates in this column
            duplicates_mask = col_series.duplicated(keep=False)

            if duplicates_mask.any():
                # Get duplicate values and their positions
                duplicate_values = col_series[duplicates_mask]
                unique_duplicate_values = duplicate_values.unique()

                column_duplicates[column] = duplicates_mask
                duplicate_info[column] = {
                    "count": duplicates_mask.sum(),
                    "unique_duplicate_values": unique_duplicate_values,
                    "duplicate_positions": duplicate_values.index.tolist(),
                }

        return column_duplicates, duplicate_info

    def process_single_file(self, file_path):
        """Process a single file for duplicates."""
        try:
            file_path = Path(file_path)
            mode = self.detection_mode.get()
            self.log(
                f"Processing: {file_path.name} (Mode: {mode.replace('_', ' ').title()} Detection)"
            )

            # Read file based on extension
            if file_path.suffix.lower() == ".csv":
                df = pd.read_csv(file_path)
            elif file_path.suffix.lower() in [".xlsx", ".xls"]:
                df = pd.read_excel(file_path)
            else:
                self.log(f"Unsupported file format: {file_path.suffix}")
                return

            if mode == "row":
                # Row duplicate detection (original functionality)
                duplicates = df.duplicated(keep=False)
                duplicate_count = duplicates.sum()
                total_items = len(df)
                item_type = "rows"

                self.log(
                    f"Found {duplicate_count} duplicate {item_type} out of {total_items} total {item_type}"
                )

                # Add a column to mark duplicates
                df["is_duplicate_row"] = duplicates

                # Create output filename
                output_filename = f"{file_path.stem}_row_duplicates_detected.csv"
                output_path = Path(self.output_directory.get()) / output_filename

                # Save as CSV
                df.to_csv(output_path, index=False)
                self.log(f"Saved: {output_filename}")

                # Log duplicate information
                if duplicate_count > 0:
                    self.log(f"Duplicate rows in {file_path.name}:")
                    duplicate_rows = df[duplicates].drop("is_duplicate_row", axis=1)
                    for idx, row in duplicate_rows.iterrows():
                        row_str = " | ".join(
                            [f"{col}: {val}" for col, val in row.items()][:3]
                        )  # Show first 3 columns
                        self.log(f"  Row {idx + 1}: {row_str}...")
                else:
                    self.log(f"No duplicate rows found in {file_path.name}")

            elif mode == "column":
                # Column duplicate detection (identical columns)
                duplicate_column_names, duplicate_cols = self.detect_duplicate_columns(
                    df
                )
                duplicate_count = len(duplicate_column_names)
                total_items = len(df.columns)
                item_type = "columns"

                self.log(
                    f"Found {duplicate_count} duplicate {item_type} out of {total_items} total {item_type}"
                )

                # Create a new dataframe with duplicate column information
                result_df = df.copy()

                # Add a row at the top to indicate which columns are duplicates
                duplicate_indicator = []
                for col in df.columns:
                    if col in duplicate_column_names:
                        duplicate_indicator.append("DUPLICATE_COLUMN")
                    else:
                        duplicate_indicator.append("UNIQUE_COLUMN")

                # Insert the indicator row at the top
                new_row = pd.DataFrame([duplicate_indicator], columns=df.columns)
                result_df = pd.concat([new_row, result_df], ignore_index=True)

                # Create output filename
                output_filename = f"{file_path.stem}_column_duplicates_detected.csv"
                output_path = Path(self.output_directory.get()) / output_filename

                # Save as CSV
                result_df.to_csv(output_path, index=False)
                self.log(f"Saved: {output_filename}")

                # Log duplicate information
                if duplicate_count > 0:
                    self.log(f"Duplicate columns in {file_path.name}:")
                    for col_name in duplicate_column_names:
                        self.log(f"  Column: {col_name}")

                    # Group duplicate columns
                    duplicate_groups = {}
                    processed_cols = set()

                    for col in duplicate_column_names:
                        if col in processed_cols:
                            continue

                        # Find all columns identical to this one
                        identical_cols = []
                        col_data = df[col]

                        for other_col in df.columns:
                            if other_col != col and df[other_col].equals(col_data):
                                identical_cols.append(other_col)

                        if identical_cols:
                            group = [col] + identical_cols
                            duplicate_groups[f"Group {len(duplicate_groups) + 1}"] = (
                                group
                            )
                            processed_cols.update(group)

                    if duplicate_groups:
                        self.log("Duplicate column groups:")
                        for group_name, cols in duplicate_groups.items():
                            self.log(f"  {group_name}: {', '.join(cols)}")
                else:
                    self.log(f"No duplicate columns found in {file_path.name}")

            else:  # column_values mode
                # Duplicate values within columns detection
                column_duplicates, duplicate_info = (
                    self.detect_duplicate_values_in_columns(df)
                )

                if column_duplicates:
                    total_duplicate_values = sum(
                        info["count"] for info in duplicate_info.values()
                    )
                    self.log(
                        f"Found duplicate values in {len(column_duplicates)} columns with {total_duplicate_values} total duplicate entries"
                    )

                    # Create result dataframe with duplicate marking for each column
                    result_df = df.copy()

                    for column, duplicates_mask in column_duplicates.items():
                        result_df[f"{column}_is_duplicate"] = duplicates_mask

                    # Create output filename
                    output_filename = (
                        f"{file_path.stem}_column_values_duplicates_detected.csv"
                    )
                    output_path = Path(self.output_directory.get()) / output_filename

                    # Save as CSV
                    result_df.to_csv(output_path, index=False)
                    self.log(f"Saved: {output_filename}")

                    # Log detailed duplicate information
                    self.log(f"Duplicate values details for {file_path.name}:")
                    for column, info in duplicate_info.items():
                        self.log(
                            f"  Column '{column}': {info['count']} duplicate entries"
                        )
                        self.log(
                            f"    Duplicate values: {list(info['unique_duplicate_values'])}"
                        )

                        # Show sample positions for each duplicate value
                        for dup_val in info["unique_duplicate_values"]:
                            positions = df[df[column] == dup_val].index.tolist()
                            self.log(
                                f"    Value '{dup_val}' appears at rows: {[pos + 1 for pos in positions[:5]]}"
                                + (
                                    f" (and {len(positions) - 5} more)"
                                    if len(positions) > 5
                                    else ""
                                )
                            )
                else:
                    self.log(
                        f"No duplicate values found within any columns in {file_path.name}"
                    )

                    # Still create output file but without duplicate markers
                    output_filename = (
                        f"{file_path.stem}_column_values_duplicates_detected.csv"
                    )
                    output_path = Path(self.output_directory.get()) / output_filename
                    df.to_csv(output_path, index=False)
                    self.log(f"Saved: {output_filename}")

            self.log("-" * 50)

        except Exception as e:
            self.log(f"Error processing {file_path.name}: {str(e)}")

    def process_files(self):
        """Process all selected files."""
        try:
            mode = self.detection_mode.get()
            mode_display = mode.replace("_", " ").title()
            self.log(f"Starting {mode_display} duplicate detection process...")
            self.log(f"Processing {len(self.input_files)} file(s)")
            self.log("=" * 50)

            for file_path in self.input_files:
                self.process_single_file(file_path)

            self.log("=" * 50)
            self.log("Duplicate detection completed!")
            self.log(f"Output files saved to: {self.output_directory.get()}")

            if mode == "row":
                info_text = (
                    f"Processing completed!\n\n"
                    f"Processed {len(self.input_files)} file(s)\n"
                    f"Output saved to: {self.output_directory.get()}\n\n"
                    f"Each output CSV file includes an 'is_duplicate_row' column "
                    f"where TRUE indicates duplicate rows."
                )
            elif mode == "column":
                info_text = (
                    f"Processing completed!\n\n"
                    f"Processed {len(self.input_files)} file(s)\n"
                    f"Output saved to: {self.output_directory.get()}\n\n"
                    f"Each output CSV file has a header row indicating "
                    f"'DUPLICATE_COLUMN' or 'UNIQUE_COLUMN' for each column."
                )
            else:  # column_values
                info_text = (
                    f"Processing completed!\n\n"
                    f"Processed {len(self.input_files)} file(s)\n"
                    f"Output saved to: {self.output_directory.get()}\n\n"
                    f"Each output CSV file includes '[ColumnName]_is_duplicate' columns "
                    f"indicating duplicate values within each column."
                )

            messagebox.showinfo("Success", info_text)

        except Exception as e:
            error_msg = f"An error occurred during processing: {str(e)}"
            self.log(error_msg)
            messagebox.showerror("Error", error_msg)

        finally:
            # Re-enable the process button and stop progress bar
            self.process_button.config(state=tk.NORMAL)
            self.progress.stop()

    def start_processing(self):
        """Start the duplicate detection process in a separate thread."""
        if not self.validate_inputs():
            return

        # Disable the process button and start progress bar
        self.process_button.config(state=tk.DISABLED)
        self.progress.start()

        # Clear previous logs
        self.log_text.delete(1.0, tk.END)

        # Start processing in a separate thread to keep GUI responsive
        processing_thread = threading.Thread(target=self.process_files)
        processing_thread.daemon = True
        processing_thread.start()


def main():
    """Main function to run the GUI application."""
    root = tk.Tk()

    # Set style
    style = ttk.Style()
    if "clam" in style.theme_names():
        style.theme_use("clam")

    DuplicateDetectorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
