from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Project root directory
BASE_DIR = Path(__file__).resolve().parents[1]

# Data directories
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"

# PostgreSQL configuration
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "shopwise"