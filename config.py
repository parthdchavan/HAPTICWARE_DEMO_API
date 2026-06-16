import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SECRET_TOKEN = os.getenv("SECRET_TOKEN")
