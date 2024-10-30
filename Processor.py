import os
from tkinter import filedialog
import pandas as pd
import openpyxl
import tabula

class DataProcessor:
    def process(self, file_path_1, file_path_2, output_type):
        data_1 = self.load_data(file_path_1)
        data_2 = self.load_data(file_path_2)

        combined_data = pd.concat([data_1, data_2], ignore_index=True)
        duplicates_removed = combined_data.drop_duplicates()

        # Ask user to select output folder and create default folder if not selected
        output_folder = self.select_output_folder()
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        output_file_name = f"output({os.path.basename(file_path_1)} & {os.path.basename(file_path_2)})"
        output_file = os.path.join(output_folder, output_file_name)

        if output_type == 'Excel':
            output_file += '.xlsx'
            duplicates_removed.to_excel(output_file, index=False)
        else:
            output_file += '.csv'
            duplicates_removed.to_csv(output_file, index=False)

        duplicates_count = len(combined_data) - len(duplicates_removed)
        return True, duplicates_removed, duplicates_count

    def process_single(self, file_path, output_type):
        data = self.load_data(file_path)
        duplicates_removed = data.drop_duplicates()

        output_folder = self.select_output_folder()
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        output_file_name = f"output({os.path.basename(file_path)})"
        output_file = os.path.join(output_folder, output_file_name)

        if output_type == 'Excel':
            output_file += '.xlsx'
            duplicates_removed.to_excel(output_file, index=False)
        else:
            output_file += '.csv'
            duplicates_removed.to_csv(output_file, index=False)

        duplicates_count = len(data) - len(duplicates_removed)
        return True, duplicates_removed, duplicates_count

    def load_data(self, file_path):
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            return pd.read_excel(file_path)
        elif file_path.endswith('.pdf'):
            return self.extract_pdf(file_path)
        else:
            raise ValueError(f"Unsupported file format for {file_path}")

    def extract_pdf(self, file_path):
        tables = tabula.read_pdf(file_path, pages='all', multiple_tables=False)
        if tables and len(tables) > 0:
            return tables[0]
        else:
            raise ValueError(f"No tables found in PDF: {file_path}")

    def select_output_folder(self):
        return filedialog.askdirectory()
