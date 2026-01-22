"""import asyncio
from connections import engine

async def connection():
    async with engine.begin() as conn:
        print("Successfull")

asyncio.run(connection())
import os
print(os.getenv("GEMINI_API_KEY"))

from openai import OpenAI 
client = OpenAI(api_key="AIzaSyA8EUh8m7QdzvVf_DfhProqyFtViY_YDhk")
models = client.models.list()
for model in models.data:
    print(model.id, model.supported_usage)"""

