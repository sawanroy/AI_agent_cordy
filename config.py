import os
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVtvly-dev-cU1Sr2M64oR3GubwekD4B7SHajgE59piILY_API_KEY")
OLLAMA_MODEL = "llama3"
DB_NAME = "cordyceps_intel"
DB_USER = "postgres"
DB_PASSWORD = "Root"
DB_HOST = "localhost"
DB_PORT = "5432"
