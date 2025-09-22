# utils.py
from pathlib import Path
from dotenv import load_dotenv
from config import PROJECT_ROOT

def init_env() -> None:
    """
    Load environment variables from a .env file if present.
    Keeps app.py clean.
    """
    load_dotenv(PROJECT_ROOT / ".env")
