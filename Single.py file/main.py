import os
import threading
from tkinter import filedialog, Frame, Label
import customtkinter as ctk
import pandas as pd
import tabula
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle


class DataProcessor:
    @staticmethod
    def process_files(file_paths, output_type):
        """Process multiple files, combining data, removing duplicates, and saving in the specified output format."""
        all_data = pd.DataFrame()
        for file_path in file_paths:
            data = DataProcessor.load_data(file_path)
            all_data = pd.concat([all_data, data], ignore_index=True)

        duplicates_removed = all_data.drop_duplicates()
        duplicates_count = len(all_data) - len(duplicates_removed)

        output_folder = DataProcessor.select_output_folder()
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        output_file = os.path.join(output_folder, f"output_combined_files.{output_type.lower()}")
        DataProcessor.save_output(duplicates_removed, output_file, output_type)

        return True, duplicates_removed, duplicates_count

    @staticmethod
    def load_data(file_path):
        """Load data from supported file types."""
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            return pd.read_excel(file_path)
        elif file_path.endswith('.pdf'):
            return DataProcessor.extract_pdf(file_path)
        else:
            raise ValueError(f"Unsupported file format for {file_path}")

    @staticmethod
    def extract_pdf(file_path):
        tables = tabula.read_pdf(file_path, pages='all', multiple_tables=False)
        if tables:
            return tables[0]
        else:
            raise ValueError(f"No tables found in PDF: {file_path}")

    @staticmethod
    def select_output_folder():
        folder = filedialog.askdirectory()
        if not folder:
            raise ValueError("Output folder not selected")
        return folder

    @staticmethod
    def save_output(data_frame, output_file, output_type):
        if output_type == 'Excel':
            data_frame.to_excel(output_file, index=False)
        elif output_type == 'CSV':
            data_frame.to_csv(output_file, index=False)
        elif output_type == 'PDF':
            DataProcessor.convert_to_pdf(data_frame, output_file)

    @staticmethod
    def convert_to_pdf(data_frame, output_file):
        pdf_file = f"{output_file}.pdf"
        col_widths = [max(len(str(col)) * 0.15 * inch, 1 * inch) for col in data_frame.columns]
        total_width = sum(col_widths)

        doc = SimpleDocTemplate(pdf_file, pagesize=(total_width, letter[1]))
        data = [data_frame.columns.tolist()] + data_frame.astype(str).values.tolist()
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        doc.build([table])
        print(f"Converted to PDF: {pdf_file}")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.file_paths = []
        self.option_output_type = None
        self.label_result = None
        self.btn_select_file_1 = None
        self.btn_select_file_2 = None

        # Overriding default title bar
        self.overrideredirect(True)
        self.update()

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

        # Container frame for main content and title bar
        self.main_frame = ctk.CTkFrame(self, fg_color=self.current_theme["bg"])
        self.main_frame.pack(fill="both", expand=True)

        # Title bar
        self.setup_title_bar()

        # App content frame
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color=self.current_theme["bg"])
        self.content_frame.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Set up the widgets in the content frame
        self.setup_widgets()

        # Initial theme application
        self.apply_theme(self.current_theme)

    def configure_app(self):
        self.geometry("500x400+100+100")
        self.title("Duplicate Detection App")
        self.resizable(True, True)

    def setup_title_bar(self):
        self.title_bar = Frame(self.main_frame, bg=self.current_theme["button_bg"], height=30)
        self.title_bar.grid(row=0, column=0, sticky="ew")

        self.title_label = Label(self.title_bar, text="Duplicate Detection App", bg=self.current_theme["button_bg"],
                                 fg="white", font=("Arial", 12, "bold"))
        self.title_label.pack(side="left", padx=10)

        self.btn_close = ctk.CTkButton(self.title_bar, text="✕", width=10, command=self.quit,
                                       fg_color=self.current_theme["button_bg"], text_color="white")
        self.btn_close.pack(side="right")

        # Toggle theme button with animation phases
        self.dark_to_light_phases = ["🌑", "🌒", "🌓", "🌔", "🌕"]
        self.light_to_dark_phases = ["🌕", "🌖", "🌗", "🌘", "🌑"]
        self.current_phase_index = 0
        self.animating = False
        self.btn_toggle_theme = ctk.CTkButton(self.title_bar, text=self.dark_to_light_phases[self.current_phase_index],
                                              width=20, command=self.toggle_theme,
                                              fg_color=self.current_theme["button_bg"], text_color="white")
        self.btn_toggle_theme.pack(side="right", padx=(0, 10))

        # Make title bar draggable
        self.title_bar.bind("<Button-1>", self.make_draggable)
        self.title_bar.bind("<B1-Motion>", self.on_drag)

    def setup_widgets(self):
        # Centering frame within content_frame for alignment
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(8, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # File 1 and File 2 selection buttons
        self.btn_select_file_1 = ctk.CTkButton(self.content_frame, text="Select File 1", command=self.select_file_1,
                                               width=150,  # Fixed width
                                               fg_color=self.current_theme["button_bg"],
                                               hover_color=self.current_theme["button_hover"],
                                               text_color=self.current_theme["button_text"])
        self.btn_select_file_1.grid(row=1, column=0, pady=(5, 5), sticky="n")

        self.label_file_1 = ctk.CTkLabel(self.content_frame, text="No file selected",
                                         fg_color=self.current_theme["bg"],
                                         text_color=self.current_theme["fg"])
        self.label_file_1.grid(row=2, column=0, pady=(0, 10), sticky="n")

        self.btn_select_file_2 = ctk.CTkButton(self.content_frame, text="Select File 2", command=self.select_file_2,
                                               width=150,  # Fixed width
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
                                              width=150,  # Fixed width
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
                                         width=150,  # Fixed width
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
        self.title_bar.configure(bg=theme["button_bg"])
        self.title_label.configure(bg=theme["button_bg"], fg="white")
        self.btn_close.configure(fg_color=theme["button_bg"], text_color="white")
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
                status, processed_data, duplicates_count = DataProcessor.process_files(self.file_paths, output_type)
                result_text = f"Processing complete. Duplicates removed: {duplicates_count}" if status else "Processing failed"
                result_color = "green" if status else "red"
                self.after(0, lambda: self.update_label_result(result_text, result_color))
            except Exception as e:
                self.after(0, lambda: self.update_label_result(f"Error: {str(e)}", "red"))

        threading.Thread(target=thread_process).start()

    def make_draggable(self, event):
        self.start_x, self.start_y = event.x, event.y

    def on_drag(self, event):
        x = self.winfo_pointerx() - self.start_x
        y = self.winfo_pointery() - self.start_y
        self.geometry(f"+{x}+{y}")


if __name__ == "__main__":
    app = App()
    app.mainloop()