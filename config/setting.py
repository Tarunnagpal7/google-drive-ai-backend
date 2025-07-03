from dotenv import load_dotenv
import os

def load_env():
    load_dotenv()

    # key = os.environ.get("OPENAI_API_KEY")
    # if not key or not key.startswith("sk-"):
    #     raise Exception("❌ OPENAI_API_KEY not set correctly in environment")
