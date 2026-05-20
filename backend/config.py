from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

PROJECT_NAME = "AOIP Platform"
VERSION = "1.0.0"
DEBUG = True
