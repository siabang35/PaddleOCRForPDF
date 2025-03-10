"""Configuration settings for the ETL pipeline."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "input"
PROCESSED_DIR = DATA_DIR / "processed"
LOG_DIR = BASE_DIR / "logs"

# Ensure directories exist
for directory in [INPUT_DIR, PROCESSED_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# OCR configuration
OCR_LANG = "en"
OCR_USE_ANGLE_CLS = True
PDF_DPI = 300

# Chart detection configuration
CHART_DETECTION = {
    "CANNY_THRESHOLD1": 50,
    "CANNY_THRESHOLD2": 150,
    "HOUGH_THRESHOLD": 100,
    "MIN_LINE_LENGTH": 100,
    "MAX_LINE_GAP": 20,
}

# Model paths
SPACY_MODEL = "en_core_web_sm"
BERT_MODEL = "all-MiniLM-L6-v2"