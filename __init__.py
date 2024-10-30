import logging
from Processor import DataProcessor
from utils import detect_columns, remove_row_duplicates

# Set up basic logging for the package
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Allow easy import access when src is imported
__all__ = ['DataProcessor', 'detect_columns', 'remove_row_duplicates']