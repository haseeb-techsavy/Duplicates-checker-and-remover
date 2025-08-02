#!/usr/bin/env python3
"""
Duplicate Row Detector with GUI
Detects duplicate rows in CSV and Excel files and outputs CSV files with duplicate marking.
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
        self.root.title("Duplicate Row Detector")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)

        # Variables
        self.input_files = []
        self.output_directory = tk.StringVar()

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
            main_frame, text="Duplicate Row Detector", font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Input Files Section
        ttk.Label(main_frame, text="Input Files:", font=("Arial", 12, "bold")).grid(
            row=1, column=0, sticky=tk.W, pady=(0, 5)
        )

        # Files listbox with scrollbar
        files_frame = ttk.Frame(main_frame)
        files_frame.grid(
            row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10)
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
        file_buttons_frame.grid(row=3, column=0, columnspan=3, pady=(0, 20))

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
        ).grid(row=4, column=0, sticky=tk.W, pady=(10, 5))

        output_frame = ttk.Frame(main_frame)
        output_frame.grid(
            row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20)
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
        self.process_button.grid(row=6, column=0, columnspan=3, pady=(0, 20))

        # Progress Bar
        self.progress = ttk.Progressbar(main_frame, mode="indeterminate")
        self.progress.grid(
            row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10)
        )

        # Status/Log Area
        ttk.Label(main_frame, text="Processing Log:", font=("Arial", 12, "bold")).grid(
            row=8, column=0, sticky=tk.W, pady=(10, 5)
        )

        self.log_text = scrolledtext.ScrolledText(main_frame, height=12, width=70)
        self.log_text.grid(
            row=9, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10)
        )

        # Configure grid weights for resizing
        main_frame.rowconfigure(9, weight=1)

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

    def process_single_file(self, file_path):
        """Process a single file for duplicates."""
        try:
            file_path = Path(file_path)
            self.log(f"Processing: {file_path.name}")

            # Read file based on extension
            if file_path.suffix.lower() == ".csv":
                df = pd.read_csv(file_path)
            elif file_path.suffix.lower() in [".xlsx", ".xls"]:
                df = pd.read_excel(file_path)
            else:
                self.log(f"Unsupported file format: {file_path.suffix}")
                return

            # Detect duplicates
            duplicates = df.duplicated(keep=False)
            duplicate_count = duplicates.sum()
            total_rows = len(df)

            self.log(
                f"Found {duplicate_count} duplicate rows out of {total_rows} total rows"
            )

            # Add a column to mark duplicates
            df["is_duplicate"] = duplicates

            # Create output filename
            output_filename = f"{file_path.stem}_duplicates_detected.csv"
            output_path = Path(self.output_directory.get()) / output_filename

            # Save as CSV
            df.to_csv(output_path, index=False)
            self.log(f"Saved: {output_filename}")

            # Log duplicate information
            if duplicate_count > 0:
                self.log(f"Duplicate rows in {file_path.name}:")
                duplicate_rows = df[duplicates].drop("is_duplicate", axis=1)
                for idx, row in duplicate_rows.iterrows():
                    row_str = " | ".join(
                        [f"{col}: {val}" for col, val in row.items()][:3]
                    )  # Show first 3 columns
                    self.log(f"  Row {idx + 1}: {row_str}...")
            else:
                self.log(f"No duplicates found in {file_path.name}")

            self.log("-" * 50)

        except Exception as e:
            self.log(f"Error processing {file_path.name}: {str(e)}")

    def process_files(self):
        """Process all selected files."""
        try:
            self.log("Starting duplicate detection process...")
            self.log(f"Processing {len(self.input_files)} file(s)")
            self.log("=" * 50)

            for file_path in self.input_files:
                self.process_single_file(file_path)

            self.log("=" * 50)
            self.log("Duplicate detection completed!")
            self.log(f"Output files saved to: {self.output_directory.get()}")

            messagebox.showinfo(
                "Success",
                f"Processing completed!\n\n"
                f"Processed {len(self.input_files)} file(s)\n"
                f"Output saved to: {self.output_directory.get()}\n\n"
                f"Each output CSV file includes an 'is_duplicate' column "
                f"where TRUE indicates duplicate rows.",
            )

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
