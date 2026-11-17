#!/usr/bin/env python3
"""Test JSON mode with different models"""

from openai import OpenAI
import os
from dotenv import load_dotenv
import json

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("ERROR: No API key found")
    exit(1)

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key
)

# Models to test
models = [
    "groq/compound-mini",
    "groq/compound",
    "qwen/qwen3.6-27b",
]

test_prompt = """Extract the job requirements from this job description as a JSON object with keys: skills, experience, education.
Job: Senior Software Engineer with 5+ years Python experience and BS Computer Science."""

for model in models:
    try:
        print(f"Testing {model}...", end=" ")
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": test_prompt}],
            response_format={"type": "json_object"},
            max_tokens=200
        )
        print(f"✓ SUCCESS")
        print(f"  Response: {response.choices[0].message.content[:100]}")
    except Exception as e:
        print(f"✗ FAILED: {type(e).__name__}")
