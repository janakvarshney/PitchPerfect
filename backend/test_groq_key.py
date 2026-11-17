#!/usr/bin/env python3
"""Test Groq API key directly"""

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
print(f"API Key (first 20 chars): {api_key[:20] if api_key else 'NOT SET'}")
print(f"API Key length: {len(api_key) if api_key else 0}")
print(f"API Key has trailing spaces: {api_key != api_key.strip() if api_key else 'N/A'}")

if not api_key:
    print("ERROR: No API key found in .env file")
    exit(1)

try:
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key
    )
    
    print("\nTesting API call to Groq...")
    response = client.chat.completions.create(
        model="compound-mini",
        messages=[
            {"role": "user", "content": "Hello"}
        ],
        max_tokens=10
    )
    print(f"✓ SUCCESS! Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"✗ FAILED: {type(e).__name__}: {e}")
    exit(1)
