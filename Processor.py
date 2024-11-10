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
        """Process multiple files, combining data, removing duplicates on common fields, and saving in the specified output format."""
        all_data = pd.DataFrame()
        file_columns = []

        # Load and concatenate data from all files
        for file_path in file_paths:
            data = DataProcessor.load_data(file_path)
            data = DataProcessor.preprocess_data(data)
            file_columns.append(set(data.columns))
            all_data = pd.concat([all_data, data], ignore_index=True)

        # Dynamically detect columns using fuzzy matching
        owner_columns = DataProcessor.find_similar_columns("Owner", all_data.columns)
        phone_columns = DataProcessor.find_similar_columns("Phone", all_data.columns)
        name_columns = [col for col in all_data.columns if col in ["First Name", "Last Name"]]
        email_columns = DataProcessor.find_similar_columns("Email", all_data.columns)

        # Define fixed columns we always want to include if present
        fixed_columns = ['Id', 'Address', 'City', 'State', 'Zip', 'County']

        # Combine all detected columns to form the final output structure
        columns_to_keep = (
                fixed_columns + sorted(owner_columns) + sorted(phone_columns) +
                sorted(name_columns) + sorted(email_columns)
        )

        # Identify common columns across all files for duplicate detection
        common_columns = set.intersection(*file_columns)
        common_columns = common_columns.intersection(columns_to_keep)

        # Apply weighted duplicate detection for more flexible matching
        duplicates_removed = DataProcessor.detect_duplicates(all_data, common_columns)

        # Keep only the specified columns in the final output, filling missing columns as needed
        filtered_data = duplicates_removed.reindex(columns=columns_to_keep).fillna("")

        duplicates_count = len(all_data) - len(duplicates_removed)

        output_folder = DataProcessor.select_output_folder()
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        output_file = os.path.join(output_folder, f"output_combined_files.{output_type.lower()}")
        DataProcessor.save_output(filtered_data, output_file, output_type)

        return True, filtered_data, duplicates_count

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
    def preprocess_data(data):
        """Standardize text, remove special characters, and normalize fields."""
        data = data.apply(lambda col: col.str.strip().str.lower() if col.dtype == 'object' else col)
        data.replace(regex=[r"[^\w\s]", r"\s+"], value="", inplace=True)
        return data

    @staticmethod
    def find_similar_columns(target_col, columns, threshold=80):
        """Find columns similar to target_col in columns with a score above the threshold."""
        return [col for col in columns if fuzz.partial_ratio(target_col.lower(), col.lower()) >= threshold]

    @staticmethod
    def detect_duplicates(data, common_columns):
        """Detect duplicates, accounting for swapped or missing alternate phone and email fields."""
        if not common_columns:
            return data.drop_duplicates()

        # Define specific column names for phone and email
        phone_cols = DataProcessor.find_similar_columns("Phone", data.columns)
        email_cols = DataProcessor.find_similar_columns("Email", data.columns)

        def is_duplicate(row1, row2):
            """Determine if two rows are duplicates, considering swapped or missing alternate fields."""
            # Check for equality in non-contact fields
            for col in common_columns - set(phone_cols) - set(email_cols):
                if row1[col] != row2[col]:
                    return False

            # Check for swapped or missing alternate phone
            for col_set in [phone_cols, email_cols]:
                if len(col_set) == 2:
                    primary, alternate = col_set
                    # Extract values for comparison
                    values1 = {row1[primary], row1[alternate]} - {""}
                    values2 = {row2[primary], row2[alternate]} - {""}

                    # Check if values match as sets, allowing for swapped or single-field scenarios
                    if not (values1 == values2 or values1.issubset(values2) or values2.issubset(values1)):
                        return False

            return True

        # Iterate over rows and mark duplicates based on custom criteria
        duplicates = []
        for i in range(len(data)):
            for j in range(i + 1, len(data)):
                if is_duplicate(data.iloc[i], data.iloc[j]):
                    duplicates.append(j)

        # Drop marked duplicate rows
        return data.drop(duplicates, axis=0).reset_index(drop=True)

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

