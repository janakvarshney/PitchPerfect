#!/usr/bin/env python3
"""List available Groq models"""

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("ERROR: No API key found in .env file")
    exit(1)

try:
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key
    )
    
    print("Available Groq models:")
    models = client.models.list()
    
    for model in models.data:
        print(f"  - {model.id}")
    
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    exit(1)
