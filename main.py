import os
import threading
from tkinter import filedialog, Frame, Label
import customtkinter as ctk
from Processor import DataProcessor


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.option_output_type = None
        self.label_result = None
        self.btn_process = None
        self.btn_select_file_2 = None
        self.label_file_2 = None
        self.label_file_1 = None
        self.btn_select_file_1 = None
        self.y = None
        self.x = None

        # Remove the default title bar
        #self.overrideredirect(True)

        # Initialize data processor and theme variables
        self.file_path_1 = ''
        self.file_path_2 = ''
        self.data_processor = DataProcessor()  # Assume this is defined elsewhere
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

        # Set up the window
        self.configure_app()

        # Main container frame to hold title bar and main content
        self.main_frame = ctk.CTkFrame(self, fg_color=self.current_theme["bg"])
        self.main_frame.pack(fill="both", expand=True)

        # Title bar setup inside main frame
        self.title_bar = Frame(self.main_frame, bg=self.current_theme["button_bg"], relief="raised", bd=0, height=30)
        self.title_bar.grid(row=0, column=0, sticky="ew")

        self.title_label = Label(self.title_bar, text="Duplicate Detection App", bg=self.current_theme["button_bg"],
                                 fg="white", font=("Arial", 12, "bold"))
        self.title_label.pack(side="left", padx=10)

        # Close and minimize buttons
        self.btn_close = ctk.CTkButton(self.title_bar, text="✕", width=10, command=self.quit,
                                       fg_color=self.current_theme["button_bg"], text_color="white")
        self.btn_close.pack(side="right")
        self.btn_minimize = ctk.CTkButton(self.title_bar, text="—", width=10, command=self.iconify,
                                          fg_color=self.current_theme["button_bg"], text_color="white")
        self.btn_minimize.pack(side="right", padx=(0, 10))

        # Dark mode toggle button
        self.current_phase_index = 0  # Initial phase index for toggle button
        self.moon_phases_dark = ["🌑", "🌒", "🌓", "🌔", "🌕"]
        self.btn_toggle_theme = ctk.CTkButton(self.title_bar, text=self.moon_phases_dark[self.current_phase_index],
                                              width=20, command=self.toggle_theme,
                                              fg_color=self.current_theme["button_bg"], text_color="white")
        self.btn_toggle_theme.pack(side="right", padx=(0, 10))

        # Make title bar draggable
        self.title_bar.bind("<Button-1>", self.make_draggable)
        self.title_bar.bind("<B1-Motion>", self.on_drag)

        # App content frame
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color=self.current_theme["bg"])
        self.content_frame.grid(row=1, column=0, sticky="nsew", pady=(10, 0))

        # Configure grid weights
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Setup widgets within content frame
        self.setup_widgets()

        # Apply the initial theme (dark theme)
        self.apply_theme(self.current_theme)

    def configure_app(self):
        self.geometry("500x400")
        self.title("Duplicate Detection App")
        self.resizable(False, False)

    def setup_widgets(self):
        # File 1 selection button and label
        self.btn_select_file_1 = ctk.CTkButton(self.content_frame, text="Select File 1", command=self.select_file_1,
                                               fg_color=self.current_theme["button_bg"],
                                               hover_color=self.current_theme["button_hover"],
                                               text_color=self.current_theme["button_text"])
        self.btn_select_file_1.pack(pady=10)

        self.label_file_1 = ctk.CTkLabel(self.content_frame, text="No file selected", fg_color=self.current_theme["bg"],
                                         text_color=self.current_theme["fg"])
        self.label_file_1.pack()

        # File 2 selection button and label
        self.btn_select_file_2 = ctk.CTkButton(self.content_frame, text="Select File 2", command=self.select_file_2,
                                               fg_color=self.current_theme["button_bg"],
                                               hover_color=self.current_theme["button_hover"],
                                               text_color=self.current_theme["button_text"])
        self.btn_select_file_2.pack(pady=10)

        self.label_file_2 = ctk.CTkLabel(self.content_frame, text="No file selected", fg_color=self.current_theme["bg"],
                                         text_color=self.current_theme["fg"])
        self.label_file_2.pack()

        # Output type selection
        self.option_output_type = ctk.CTkComboBox(self.content_frame,
                                                  values=["Excel", "CSV", "PDF"])  # Added PDF here
        self.option_output_type.set("Excel")  # Set default value
        self.option_output_type.pack(pady=10)

        # Process button
        self.btn_process = ctk.CTkButton(self.content_frame, text="Process", command=self.process_files,
                                         fg_color=self.current_theme["button_bg"],
                                         hover_color=self.current_theme["button_hover"],
                                         text_color=self.current_theme["button_text"])
        self.btn_process.pack(pady=20)

        # Result label to show processing messages
        self.label_result = ctk.CTkLabel(self.content_frame, text="", fg_color=self.current_theme["bg"],
                                         text_color=self.current_theme["fg"])
        self.label_result.pack(pady=10)

    def apply_theme(self, theme):
        # Update colors for widgets
        self.main_frame.configure(fg_color=theme["bg"])
        self.content_frame.configure(fg_color=theme["bg"])
        self.title_bar.configure(bg=theme["button_bg"])
        self.title_label.configure(bg=theme["button_bg"], fg=theme["fg"])

        # Update buttons
        self.btn_select_file_1.configure(fg_color=theme["button_bg"], hover_color=theme["button_hover"],
                                         text_color=theme["button_text"])
        self.btn_select_file_2.configure(fg_color=theme["button_bg"], hover_color=theme["button_hover"],
                                         text_color=theme["button_text"])
        self.btn_process.configure(fg_color=theme["button_bg"], hover_color=theme["button_hover"],
                                   text_color=theme["button_text"])
        self.btn_close.configure(fg_color=theme["button_bg"], text_color="white")
        self.btn_minimize.configure(fg_color=theme["button_bg"], text_color="white")
        self.btn_toggle_theme.configure(fg_color=theme["button_bg"], text_color="white")

        # Update labels
        self.label_file_1.configure(fg_color=theme["bg"], text_color=theme["fg"])
        self.label_file_2.configure(fg_color=theme["bg"], text_color=theme["fg"])

        # Update result label background color to match the theme
        self.label_result.configure(fg_color=theme["bg"], text_color=theme["fg"])

    def toggle_theme(self):
        # Switch between dark and light themes
        self.current_theme = self.light_theme if self.current_theme == self.dark_theme else self.dark_theme
        self.current_phase_index = (self.current_phase_index + 1) % len(self.moon_phases_dark)
        self.btn_toggle_theme.configure(text=self.moon_phases_dark[self.current_phase_index])
        self.apply_theme(self.current_theme)

    def select_file_1(self):
        """Select the first file and update the label."""
        self.file_path_1 = filedialog.askopenfilename()
        if self.file_path_1:
            self.label_file_1.configure(text=os.path.basename(self.file_path_1))

    def select_file_2(self):
        """Select the second file and update the label."""
        self.file_path_2 = filedialog.askopenfilename()
        if self.file_path_2:
            self.label_file_2.configure(text=os.path.basename(self.file_path_2))

    def process_files(self):
        """Process selected files to remove duplicates."""
        output_type = self.option_output_type.get()
        self.label_result.configure(text="Processing...")  # Indicate processing has started
        thread = threading.Thread(target=self.run_processing, args=(output_type,))
        thread.start()

    def run_processing(self, output_type):
        try:
            if self.file_path_1 and self.file_path_2:
                success, _, duplicates_count = DataProcessor.process(self.file_path_1, self.file_path_2, output_type)
            elif self.file_path_1:
                success, _, duplicates_count = DataProcessor.process_single(self.file_path_1, output_type)
            else:
                self.label_result.configure(text="Please select at least one file")
                return

            if success:
                self.label_result.configure(text=f"Processing complete. Duplicates removed: {duplicates_count}")
            else:
                self.label_result.configure(text="Processing failed.")
        except Exception as e:
            self.label_result.configure(text=f"Error: {str(e)}")

    def make_draggable(self, event):
        self.x = event.x
        self.y = event.y

    def on_drag(self, event):
        x = self.winfo_x() - self.x + event.x
        y = self.winfo_y() - self.y + event.y
        self.geometry(f"+{x}+{y}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
