import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SECRET_TOKEN = os.getenv("SECRET_TOKEN")

if not DATABASE_URL:
	raise ValueError("DATABASE_URL is not set. Add it to your .env file.")
