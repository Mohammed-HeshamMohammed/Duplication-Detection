import os
import threading
from tkinter import filedialog
import customtkinter as ctk
from Processor import DataProcessor

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title_label = None
        self.btn_select_files = None
        self.label_file_1 = None
        self.dark_to_light_phases = None
        self.light_to_dark_phases = None
        self.current_phase_index = None
        self.btn_toggle_theme = None
        self.label_file_2 = None
        self.btn_process = None
        self.animating = None
        self.file_paths = []
        self.option_output_type = None
        self.label_result = None
        self.btn_select_file_1 = None
        self.btn_select_file_2 = None

        # Theme settings
        self.dark_theme = {
            "bg": "#2b2b2b",
            "fg": "white",
            "button_bg": "#3A7CA5",
            "button_text": "white",
            "button_hover": "#4A9FC7"
        }
        self.light_theme = {
            "bg": "#f0f0f0",
            "fg": "black",
            "button_bg": "#3A7CA5",
            "button_text": "white",
            "button_hover": "#74B9FF"
        }
        self.current_theme = self.dark_theme

        # Setting up the app window
        self.configure_app()

        # Main frame for content
        self.main_frame = ctk.CTkFrame(self, fg_color=self.current_theme["bg"])
        self.main_frame.pack(fill="both", expand=True)

        # Add the toggle theme button to the top-right corner
        self.setup_toggle_theme_button()

        # App content frame
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color=self.current_theme["bg"])
        self.content_frame.pack(fill="both", expand=True, pady=(40, 0))

        # Set up the widgets in the content frame
        self.setup_widgets()

        # Initial theme application
        self.apply_theme(self.current_theme)

    def configure_app(self):
        self.geometry("500x400+100+100")
        self.title("Duplicate Detection App")
        self.resizable(True, True)

    def setup_toggle_theme_button(self):
        # Toggle theme button with animation phases
        self.dark_to_light_phases = ["🌑", "🌒", "🌓", "🌔", "🌕"]
        self.light_to_dark_phases = ["🌕", "🌖", "🌗", "🌘", "🌑"]
        self.current_phase_index = 0
        self.animating = False
        self.btn_toggle_theme = ctk.CTkButton(self.main_frame, text=self.dark_to_light_phases[self.current_phase_index],
                                              width=20, command=self.toggle_theme,
                                              fg_color=self.current_theme["button_bg"], text_color="white")
        self.btn_toggle_theme.place(relx=0.95, rely=0.02, anchor="ne")

    def setup_widgets(self):
        # Centering frame within content_frame for alignment
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(8, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # File 1 and File 2 selection buttons
        self.btn_select_file_1 = ctk.CTkButton(self.content_frame, text="Select File 1", command=self.select_file_1,
                                               width=150,
                                               fg_color=self.current_theme["button_bg"],
                                               hover_color=self.current_theme["button_hover"],
                                               text_color=self.current_theme["button_text"])
        self.btn_select_file_1.grid(row=1, column=0, pady=(5, 5), sticky="n")

        self.label_file_1 = ctk.CTkLabel(self.content_frame, text="No file selected",
                                         fg_color=self.current_theme["bg"],
                                         text_color=self.current_theme["fg"])
        self.label_file_1.grid(row=2, column=0, pady=(0, 10), sticky="n")

        self.btn_select_file_2 = ctk.CTkButton(self.content_frame, text="Select File 2", command=self.select_file_2,
                                               width=150,
                                               fg_color=self.current_theme["button_bg"],
                                               hover_color=self.current_theme["button_hover"],
                                               text_color=self.current_theme["button_text"])
        self.btn_select_file_2.grid(row=3, column=0, pady=(5, 5), sticky="n")

        self.label_file_2 = ctk.CTkLabel(self.content_frame, text="No file selected",
                                         fg_color=self.current_theme["bg"],
                                         text_color=self.current_theme["fg"])
        self.label_file_2.grid(row=4, column=0, pady=(0, 10), sticky="n")

        # Multi-file selection button
        self.btn_select_files = ctk.CTkButton(self.content_frame, text="Select Multiple Files",
                                              command=self.select_multiple_files,
                                              width=150,
                                              fg_color=self.current_theme["button_bg"],
                                              hover_color=self.current_theme["button_hover"],
                                              text_color=self.current_theme["button_text"])
        self.btn_select_files.grid(row=5, column=0, pady=(10, 5), sticky="n")

        # Output type selection
        self.option_output_type = ctk.CTkComboBox(self.content_frame, values=["Excel", "CSV", "PDF"], width=150)
        self.option_output_type.set("Excel")
        self.option_output_type.grid(row=6, column=0, pady=(10, 10), sticky="n")

        # Process button
        self.btn_process = ctk.CTkButton(self.content_frame, text="Process", command=self.process_files,
                                         width=150,
                                         fg_color=self.current_theme["button_bg"],
                                         hover_color=self.current_theme["button_hover"],
                                         text_color=self.current_theme["button_text"])
        self.btn_process.grid(row=7, column=0, pady=(10, 20), sticky="n")

        # Result label
        self.label_result = ctk.CTkLabel(self.content_frame, text="", fg_color=self.current_theme["bg"],
                                         text_color=self.current_theme["fg"])
        self.label_result.grid(row=8, column=0, pady=(10, 10), sticky="n")

    def apply_theme(self, theme):
        self.main_frame.configure(fg_color= theme["bg"])
        self.content_frame.configure(fg_color=theme["bg"])
        self.btn_toggle_theme.configure(fg_color=theme["button_bg"], text_color="white")

        self.label_file_1.configure(fg_color=theme["bg"], text_color=theme["fg"])
        self.label_file_2.configure(fg_color=theme["bg"], text_color=theme["fg"])
        self.label_result.configure(fg_color=theme["bg"], text_color=theme["fg"])

        self.btn_select_file_1.configure(fg_color=theme["button_bg"], text_color=theme["button_text"],
                                         hover_color=theme["button_hover"])
        self.btn_select_file_2.configure(fg_color=theme["button_bg"], text_color=theme["button_text"],
                                         hover_color=theme["button_hover"])
        self.btn_select_files.configure(fg_color=theme["button_bg"], text_color=theme["button_text"],
                                        hover_color=theme["button_hover"])
        self.btn_process.configure(fg_color=theme["button_bg"], text_color=theme["button_text"],
                                   hover_color=theme["button_hover"])

    def toggle_theme(self):
        if self.animating:
            return
        self.animating = True
        phases = self.dark_to_light_phases if self.current_theme == self.dark_theme else self.light_to_dark_phases
        for i, phase in enumerate(phases):
            self.after(i * 50, lambda p=phase: self.btn_toggle_theme.configure(text=p))
        self.after(len(phases) * 50, self.complete_toggle)

    def complete_toggle(self):
        self.current_theme = self.light_theme if self.current_theme == self.dark_theme else self.dark_theme
        self.apply_theme(self.current_theme)
        self.animating = False

    def select_file_1(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            if len(self.file_paths) >= 1:
                self.file_paths[0] = file_path  # Replace existing file
            else:
                self.file_paths.append(file_path)
            self.label_file_1.configure(text=os.path.basename(file_path))

    def select_file_2(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            if len(self.file_paths) >= 2:
                self.file_paths[1] = file_path  # Replace existing file
            else:
                self.file_paths.append(file_path)
            self.label_file_2.configure(text=os.path.basename(file_path))

    def select_multiple_files(self):
        file_paths = filedialog.askopenfilenames()
        self.file_paths.extend(file_paths)
        self.label_result.configure(text=f"{len(file_paths)} files selected")

    def update_label_result(self, text, color):
        self.label_result.configure(text=text, text_color=color)

    def process_files(self):
        if not self.file_paths or not self.option_output_type.get():
            self.label_result.configure(text="Please select files and output type", text_color="red")
            return

        output_type = self.option_output_type.get()

        def thread_process():
            try:
                success, filtered_data, duplicates_count = DataProcessor.process_files(self.file_paths, output_type)
                if success:
                    result_text = f"Processing complete. Duplicates removed: {duplicates_count}"
                    result_color = "green"
                else:
                    result_text = "Processing failed."
                    result_color = "red"

                self.after(0, lambda: self.update_label_result(result_text, result_color))

                # Clear the file paths and reset file selection labels
                self.file_paths = []
                self.after(0, lambda: self.label_file_1.configure(text="No file selected"))
                self.after(0, lambda: self.label_file_2.configure(text="No file selected"))

            except Exception as e:
                self.after(0, lambda: self.update_label_result(f"Error: {str(e)}", "red"))

        threading.Thread(target=thread_process).start()


if __name__ == "__main__":
    app = App()
    app.mainloop()
