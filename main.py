import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
from Processor import DataProcessor
from PIL import Image

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Duplicate Detection App")
        self.geometry("500x375")

        # Initialize file paths and processor
        self.file_path_1 = ""
        self.file_path_2 = ""
        self.data_processor = DataProcessor()

        # Load sun and moon icons
        self.sun_icon = ctk.CTkImage(Image.open("../icons/sun_icon.png"), size=(20, 20))
        self.moon_icon = ctk.CTkImage(Image.open("../icons/moon_icon.png"), size=(20, 20))

        # Create a Frame for the Dark/Light mode toggle at the top-right corner
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(anchor="ne", padx=10, pady=10)

        # Add Dark Mode and Light Mode toggle buttons (only one will be visible at a time)
        self.button_mode_toggle = ctk.CTkButton(top_frame, image=self.moon_icon, text="", width=40, fg_color="transparent", hover_color="transparent", command=self.switch_mode)
        self.button_mode_toggle.pack(side="left", padx=5)

        # Start in light mode
        self.light_mode = True
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
            # Show the moon icon (switch to dark mode)
            self.button_mode_toggle.configure(image=self.moon_icon)
        else:
            # Show the sun icon (switch to light mode)
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
        if not self.file_path_1 or not self.file_path_2:
            self.label_result.configure(text="Please select both files.")
            return

        output_type = self.option_output_type.get()

        # Process files and show duplicate count
        try:
            success, _, duplicates_count = self.data_processor.process(self.file_path_1, self.file_path_2, output_type)
            if success:
                self.label_result.configure(text=f"Duplicates removed: {duplicates_count}")
        except ValueError as e:
            self.label_result.configure(text=f"Error: {e}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
