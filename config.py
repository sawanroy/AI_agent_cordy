import os
import sys
import getpass
from dotenv import load_dotenv

load_dotenv()

# Read configuration from environment; avoid hard-coded secrets.
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
DB_NAME = os.getenv("DB_NAME", "cordyceps_intel")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

# If password not provided via env, prompt interactively when possible.
if not DB_PASSWORD:
	if sys.stdin.isatty():
		DB_PASSWORD = getpass.getpass("Postgres DB password: ")
	else:
		DB_PASSWORD = None
