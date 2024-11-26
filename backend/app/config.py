import os
from dotenv import load_dotenv

load_dotenv()

WKHTMLTOPDF_PATH = 'C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe'
WHISPER_MODEL = "large-v3"
WHISPER_DEVICE = "cuda"
WHISPER_COMPUTE_TYPE = "float16"
DEFAULT_OUTPUT_FOLDER = os.getenv('DEFAULT_OUTPUT_FOLDER', 'output')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')