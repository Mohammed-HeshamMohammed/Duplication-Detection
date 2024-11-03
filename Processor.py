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
    def process(file_path_1, file_path_2, output_type):
        """Process two files and return a tuple indicating success, the DataFrame, and duplicates count."""
        data_1 = DataProcessor.load_data(file_path_1)
        data_2 = DataProcessor.load_data(file_path_2)

        # Combine and remove duplicates
        combined_data = pd.concat([data_1, data_2], ignore_index=True)
        duplicates_removed = combined_data.drop_duplicates()

        output_folder = DataProcessor.select_output_folder()
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        output_file_name = f"output({os.path.basename(file_path_1)} & {os.path.basename(file_path_2)})"
        output_file = os.path.join(output_folder, output_file_name)

        if output_type == 'Excel':
            output_file += '.xlsx'
            duplicates_removed.to_excel(output_file, index=False)
        elif output_type == 'CSV':
            output_file += '.csv'
            duplicates_removed.to_csv(output_file, index=False)
        elif output_type == 'PDF':
            DataProcessor.convert_to_pdf(duplicates_removed, output_file)
            return True, duplicates_removed, None  # PDF output has no duplicates count

        duplicates_count = len(combined_data) - len(duplicates_removed)
        return True, duplicates_removed, duplicates_count

    @staticmethod
    def process_single(file_path, output_type):
        """Process a single file and return a tuple indicating success, the DataFrame, and duplicates count."""
        data = DataProcessor.load_data(file_path)
        duplicates_removed = data.drop_duplicates()

        output_folder = DataProcessor.select_output_folder()
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        output_file_name = f"output({os.path.basename(file_path)})"
        output_file = os.path.join(output_folder, output_file_name)

        if output_type == 'Excel':
            output_file += '.xlsx'
            duplicates_removed.to_excel(output_file, index=False)
        elif output_type == 'CSV':
            output_file += '.csv'
            duplicates_removed.to_csv(output_file, index=False)
        elif output_type == 'PDF':
            DataProcessor.convert_to_pdf(duplicates_removed, output_file)
            return True, duplicates_removed, None  # PDF output has no duplicates count

        duplicates_count = len(data) - len(duplicates_removed)
        return True, duplicates_removed, duplicates_count

    @staticmethod
    def load_data(file_path):
        """Load data from a given file path based on the file type."""
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
        """Extract the first table from a PDF file."""
        tables = tabula.read_pdf(file_path, pages='all', multiple_tables=False)
        if tables and len(tables) > 0:
            df = tables[0]
            return df
        else:
            raise ValueError(f"No tables found in PDF: {file_path}")

    @staticmethod
    def select_output_folder():
        """Prompt user to select an output folder."""
        return filedialog.askdirectory()

    @staticmethod
    def convert_to_pdf(data_frame, output_file):
        """Convert a DataFrame to a PDF with a table format and dynamic page sizing."""
        pdf_file = f"{output_file}.pdf"

        # Calculate the column widths with more robust type handling
        col_widths = []
        for col in data_frame.columns:
            # Convert each column to string to avoid type errors
            str_col = data_frame[col].astype(str)
            max_length = max(str_col.map(len).max(), len(col))  # Compare lengths of column names and data
            # Set a minimum column width
            col_widths.append(max(max_length * 0.15 * inch, 1 * inch))  # Minimum width of 1 inch

        # Calculate total width needed for the table
        total_width = sum(col_widths)

        # Create a SimpleDocTemplate with dynamic page size
        doc = SimpleDocTemplate(pdf_file, pagesize=(total_width, letter[1] * inch))  # Use letter height in inches

        # Create the table data
        data = [data_frame.columns.tolist()] + data_frame.astype(str).values.tolist()  # Convert all values to strings

        # Create the table
        table = Table(data, colWidths=col_widths)

        # Apply style to the table
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])
        table.setStyle(style)

        # Build the PDF
        doc.build([table])
        print(f"Converted to PDF: {pdf_file}")

