"""
Configuration file for NLU System
Update these settings for your environment
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DATABASE_HOST', 'localhost'),
    'user': os.getenv('DATABASE_USER'),  # Change this
    'password': os.getenv('DATABASE_PASSWORD'),  # Change this
    'database': os.getenv('DATABASE_NAME', 'nlu_system'),  # Change if needed
    'port': int(os.getenv('DATABASE_PORT', 3306))
}

# Module settings
SEGMENTATION_CONFIG = {
    'store_results': True,
    'min_sentence_length': 3,  # Minimum words per sentence
}

MORPHOLOGY_CONFIG = {
    'store_results': True,
    'min_word_length': 2,  # Minimum characters per word
}

# Logging configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'log_file': 'nlu_system.log'
}
