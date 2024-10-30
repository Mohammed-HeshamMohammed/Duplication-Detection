import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
from Processor import DataProcessor
from PIL import Image
import os
import sys

def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and PyInstaller """
    try:
        base_path = sys._MEIPASS  # PyInstaller temporary folder
    except Exception:
        base_path = os.path.abspath(".")

    full_path = os.path.join(base_path, "icons", relative_path)
    print(f"Loading resource from: {full_path}")  # Debug print for path verification
    return full_path



class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Duplicate Detection App")
        self.geometry("500x400")

        # Initialize file paths and processor
        self.file_path_1 = ""
        self.file_path_2 = ""
        self.data_processor = DataProcessor()

        # Load icons with the updated path
        self.sun_icon = ctk.CTkImage(Image.open(resource_path("sun_icon.png")), size=(20, 20))
        self.moon_icon = ctk.CTkImage(Image.open(resource_path("moon_icon.png")), size=(20, 20))

        # Create a Frame for the Dark/Light mode toggle at the top-right corner
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(anchor="ne", padx=10, pady=10)

        # Add Dark Mode and Light Mode toggle buttons (only one will be visible at a time)
        self.button_mode_toggle = ctk.CTkButton(
            top_frame,
            image=self.moon_icon,
            text="",
            width=40,
            fg_color="transparent",
            hover_color="lightgrey",
            command=self.switch_mode
        )
        self.button_mode_toggle.pack(side="left", padx=5)

        # Start in dark mode
        self.light_mode = False
        ctk.set_appearance_mode("dark")  # Set dark mode by default
        self.update_icon()

        # File selection buttons and labels
        self.button_browse_1 = ctk.CTkButton(self, text="Select File 1", command=self.browse_file_1)
        self.button_browse_1.pack(pady=10)

        self.label_file_1 = ctk.CTkLabel(self, text="No file selected")
        self.label_file_1.pack(pady=5)

        self.button_browse_2 = ctk.CTkButton(self, text="Select File 2", command=self.browse_file_2)
        self.button_browse_2.pack(pady=10)

        self.label_file_2 = ctk.CTkLabel(self, text="No file selected")
        self.label_file_2.pack(pady=5)

        # Format selection dropdown
        self.option_output_type = ctk.CTkComboBox(self, values=["CSV", "Excel"])
        self.option_output_type.pack(pady=10)

        # Process button
        self.button_process = ctk.CTkButton(self, text="Process Files", command=self.process_files)
        self.button_process.pack(pady=20)

        # Label to display duplicate count
        self.label_result = ctk.CTkLabel(self, text="")
        self.label_result.pack(pady=5)

    def switch_mode(self):
        """Switch between light and dark mode."""
        if self.light_mode:
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")
        self.light_mode = not self.light_mode
        self.update_icon()

    def update_icon(self):
        """Update the button icon based on the current mode."""
        if self.light_mode:
            self.button_mode_toggle.configure(image=self.moon_icon)
        else:
            self.button_mode_toggle.configure(image=self.sun_icon)

    def browse_file_1(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV, Excel and PDF files", "*.csv;*.xlsx;*.pdf")])
        if file_path:
            self.file_path_1 = file_path
            self.label_file_1.configure(text=f"Selected: {self.file_path_1.split('/')[-1]}")

    def browse_file_2(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV, Excel and PDF files", "*.csv;*.xlsx;*.pdf")])
        if file_path:
            self.file_path_2 = file_path
            self.label_file_2.configure(text=f"Selected: {self.file_path_2.split('/')[-1]}")

    def process_files(self):
        # If only one file is selected (either file 1 or file 2), handle duplicates within that file
        if self.file_path_1 and not self.file_path_2:
            output_type = self.option_output_type.get()
            try:
                success, _, duplicates_count = self.data_processor.process_single(self.file_path_1, output_type)
                if success:
                    self.label_result.configure(text=f"Duplicates removed from File 1: {duplicates_count}")
            except ValueError as e:
                self.label_result.configure(text=f"Error: {e}")
            return

        elif not self.file_path_1 and self.file_path_2:
            output_type = self.option_output_type.get()
            try:
                success, _, duplicates_count = self.data_processor.process_single(self.file_path_2, output_type)
                if success:
                    self.label_result.configure(text=f"Duplicates removed from File 2: {duplicates_count}")
            except ValueError as e:
                self.label_result.configure(text=f"Error: {e}")
            return

        # If both files are selected, handle duplicates between the two files
        if self.file_path_1 and self.file_path_2:
            output_type = self.option_output_type.get()
            try:
                success, _, duplicates_count = self.data_processor.process(self.file_path_1, self.file_path_2, output_type)
                if success:
                    self.label_result.configure(text=f"Duplicates removed between both files: {duplicates_count}")
            except ValueError as e:
                self.label_result.configure(text=f"Error: {e}")
            return

        # If no files are selected, display an error
        self.label_result.configure(text="Please select at least one file.")

    def select_output_folder(self):
        folder_selected = filedialog.askdirectory()
        return folder_selected if folder_selected else os.getcwd()

if __name__ == "__main__":
    app = App()
    app.mainloop()
