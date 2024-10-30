import pandas as pd
from fuzzywuzzy import fuzz
import openpyxl



def detect_columns(df):
    # Fuzzy matching logic for column names
    column_mapping = {
        'First Name': ['first name', 'f_name', 'fname'],
        'Last Name': ['last name', 'l_name', 'lname'],
        'Address': ['address', 'property location', 'location', 'address location']
    }

    for col in df.columns:
        for standard, variations in column_mapping.items():
            if any(fuzz.partial_ratio(col.lower(), var) > 80 for var in variations):
                df.rename(columns={col: standard}, inplace=True)

    return df


def remove_row_duplicates(df):
    initial_len = len(df)

    # Drop duplicates based on 'First Name', 'Last Name', and 'Address'
    cleaned_df = df.drop_duplicates(subset=['First Name', 'Last Name', 'Address'], keep='first')

    duplicates_removed = initial_len - len(cleaned_df)
    return cleaned_df, duplicates_removed