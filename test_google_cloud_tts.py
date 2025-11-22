#!/usr/bin/env python3
"""
Quick test for Google Cloud TTS REST API implementation
"""
import requests
import json
import base64
from pathlib import Path

# Read API key from secrets
secrets_file = Path(".streamlit/secrets.toml")
if secrets_file.exists():
    content = secrets_file.read_text()
    # Simple parsing - look for the API key line
    for line in content.split('\n'):
        if 'google_cloud_tts_api_key' in line:
            api_key = line.split('=')[1].strip().strip('"')
            break
else:
    print("❌ No .streamlit/secrets.toml found")
    exit(1)

print(f"✓ API key found: {api_key[:20]}...")

# Test the REST API
url = "https://texttospeech.googleapis.com/v1/text:synthesize"
headers = {
    "X-goog-api-key": api_key,
    "Content-Type": "application/json; charset=utf-8"
}

payload = {
    "input": {"text": "Olá, como vai você?"},
    "voice": {
        "languageCode": "pt-BR",
        "name": "pt-BR-Standard-A"
    },
    "audioConfig": {
        "audioEncoding": "MP3",
        "speakingRate": 1.0
    }
}

print("\n🔄 Testing Google Cloud TTS REST API...")
print(f"   URL: {url}")
print(f"   Text: {payload['input']['text']}")
print(f"   Voice: {payload['voice']['name']}")

response = requests.post(url, headers=headers, json=payload)

print(f"\n📊 Response status: {response.status_code}")

if response.status_code == 200:
    print("✅ SUCCESS! API call worked")
    response_data = response.json()
    audio_content_base64 = response_data.get("audioContent", "")
    audio_bytes = base64.b64decode(audio_content_base64)
    print(f"   Audio size: {len(audio_bytes)} bytes")
    
    # Save test file
    test_file = Path("test_google_cloud_tts.mp3")
    test_file.write_bytes(audio_bytes)
    print(f"   Saved to: {test_file}")
    print("\n🎵 Play the file to verify audio quality!")
else:
    print(f"❌ FAILED!")
    print(f"   Error: {response.text[:500]}")
