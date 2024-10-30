import os
import pandas as pd
import openpyxl
import tabula

class DataProcessor:
    def process_single(self, file_path, output_folder, output_type):
        # Determine the type of file (CSV, Excel, or PDF)
        if file_path.endswith('.csv'):
            data = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            data = pd.read_excel(file_path)
        elif file_path.endswith('.pdf'):
            data = self.extract_pdf(file_path)
        else:
            raise ValueError(f"Unsupported file format for {file_path}")

        # Remove duplicates
        duplicates_removed = data.drop_duplicates()

        # Create the default output folder if it doesn't exist
        if not output_folder:
            output_folder = os.path.join(os.getcwd(), "Data Outputs")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Generating the output file name
        file_name = os.path.basename(file_path).split('.')[0]
        output_file_name = f"output({file_name})"

        # Saving the result based on user-selected output type (CSV or Excel)
        if output_type == 'Excel':
            output_file_path = os.path.join(output_folder, f"{output_file_name}.xlsx")
            duplicates_removed.to_excel(output_file_path, index=False)
        else:
            output_file_path = os.path.join(output_folder, f"{output_file_name}.csv")
            duplicates_removed.to_csv(output_file_path, index=False)

        # Return success and the count of duplicates removed
        duplicates_count = len(data) - len(duplicates_removed)
        return True, duplicates_removed, duplicates_count

    def process(self, file_path_1, file_path_2, output_folder, output_type):
        # Determine the type of file for file 1 (CSV, Excel, or PDF)
        if file_path_1.endswith('.csv'):
            data_1 = pd.read_csv(file_path_1)
        elif file_path_1.endswith('.xlsx'):
            data_1 = pd.read_excel(file_path_1)
        elif file_path_1.endswith('.pdf'):
            data_1 = self.extract_pdf(file_path_1)
        else:
            raise ValueError(f"Unsupported file format for {file_path_1}")

        # Determine the type of file for file 2 (CSV, Excel, or PDF)
        if file_path_2.endswith('.csv'):
            data_2 = pd.read_csv(file_path_2)
        elif file_path_2.endswith('.xlsx'):
            data_2 = pd.read_excel(file_path_2)
        elif file_path_2.endswith('.pdf'):
            data_2 = self.extract_pdf(file_path_2)
        else:
            raise ValueError(f"Unsupported file format for {file_path_2}")

        # Merging both datasets
        combined_data = pd.concat([data_1, data_2], ignore_index=True)

        # Remove duplicates
        duplicates_removed = combined_data.drop_duplicates()

        # Create the default output folder if it doesn't exist
        if not output_folder:
            output_folder = os.path.join(os.getcwd(), "Data Outputs")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Generating the output file name
        file_name_1 = os.path.basename(file_path_1).split('.')[0]
        file_name_2 = os.path.basename(file_path_2).split('.')[0]
        output_file_name = f"output({file_name_1} & {file_name_2})"

        # Saving the result based on user-selected output type (CSV or Excel)
        if output_type == 'Excel':
            output_file_path = os.path.join(output_folder, f"{output_file_name}.xlsx")
            duplicates_removed.to_excel(output_file_path, index=False)
        else:
            output_file_path = os.path.join(output_folder, f"{output_file_name}.csv")
            duplicates_removed.to_csv(output_file_path, index=False)

        # Return success and the count of duplicates removed
        duplicates_count = len(combined_data) - len(duplicates_removed)
        return True, duplicates_removed, duplicates_count

    def extract_pdf(self, file_path):
        """Extract tables from PDF and return as pandas DataFrame."""
        try:
            tables = tabula.read_pdf(file_path, pages='all', multiple_tables=False)
            if len(tables) > 0:
                return tables[0]
            else:
                raise ValueError(f"No tables found in PDF: {file_path}")
        except Exception as e:
            raise ValueError(f"Failed to extract data from PDF {file_path}: {e}")
