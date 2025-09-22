# config.py
from pathlib import Path
# Absolute path to the project root (folder that contains app.py)
PROJECT_ROOT = Path(__file__).parent
# Model & other constants (tweak as needed)
MODEL_NAME = "gemini-1.5-flash"
PROMPTING_METHOD = 'few-shots'
