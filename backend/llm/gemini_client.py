import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY2"))
model = genai.GenerativeModel("models/gemini-3-flash-preview")





