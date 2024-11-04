import os
from tkinter import filedialog
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

