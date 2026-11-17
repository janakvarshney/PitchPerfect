#!/usr/bin/env python3
"""Test with correct model name format"""

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("ERROR: No API key found")
    exit(1)

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key
)

# Try different model name formats
models_to_try = [
    "groq/compound-mini",
    "groq/compound",
    "qwen/qwen3.6-27b",
]

for model_name in models_to_try:
    try:
        print(f"Testing {model_name}...", end=" ")
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        print(f"✓ SUCCESS")
        break
    except Exception as e:
        print(f"✗ {type(e).__name__}")
