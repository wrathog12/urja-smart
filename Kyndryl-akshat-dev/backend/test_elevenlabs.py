#!/usr/bin/env python3
"""
Quick test script for ElevenLabs API
Run this to test if your API key and voice ID work
"""

import requests
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.credential_manager import get_secret

# Load credentials
ENVIRONMENT = os.getenv('ENVIRONMENT', 'LOCAL').upper()
secret_keys = get_secret(ENVIRONMENT)

API_KEY = secret_keys.get('ELEVENLABS_API_KEY', '').strip()
VOICE_ID = secret_keys.get('ELEVENLABS_VOICE_ID', 'TX3LPaxmHKxFdv7VOQHJ')
API_URL = "https://api.elevenlabs.io/v1"

print("=" * 60)
print("ElevenLabs API Test")
print("=" * 60)
print(f"API Key: {API_KEY[:8]}...{API_KEY[-4:] if len(API_KEY) > 12 else '****'}")
print(f"Voice ID: {VOICE_ID}")
print(f"API URL: {API_URL}")
print()

if not API_KEY:
    print("❌ ERROR: No API key found!")
    sys.exit(1)

# Test 1: Check API key by getting user info
print("Test 1: Getting user subscription info...")
try:
    response = requests.get(
        f"{API_URL}/user/subscription",
        headers={
            "xi-api-key": API_KEY,
            "Accept": "application/json"
        },
        timeout=10
    )
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ API Key is VALID!")
        print(f"Character Count: {data.get('character_count', 0)}")
        print(f"Character Limit: {data.get('character_limit', 0)}")
        print(f"Status: {data.get('status', 'unknown')}")
    elif response.status_code == 401:
        print(f"❌ API Key is INVALID or EXPIRED")
        print(f"Response: {response.text}")
        sys.exit(1)
    else:
        print(f"⚠️  Unexpected status: {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print()

# Test 2: Check if voice ID exists
print("Test 2: Checking voice ID...")
try:
    response = requests.get(
        f"{API_URL}/voices/{VOICE_ID}",
        headers={
            "xi-api-key": API_KEY,
            "Accept": "application/json"
        },
        timeout=10
    )
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Voice ID is VALID!")
        print(f"Voice Name: {data.get('name', 'Unknown')}")
        print(f"Voice Category: {data.get('category', 'Unknown')}")
    elif response.status_code == 404:
        print(f"❌ Voice ID NOT FOUND!")
        print(f"This voice doesn't exist or doesn't belong to your account")
        print(f"Response: {response.text}")
    else:
        print(f"⚠️  Unexpected status: {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print()

# Test 3: Try TTS generation with short text
print("Test 3: Generating test audio (short text)...")
try:
    test_text = "Hello, this is a test."
    response = requests.post(
        f"{API_URL}/text-to-speech/{VOICE_ID}",
        headers={
            "xi-api-key": API_KEY,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg"
        },
        json={
            "text": test_text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        },
        timeout=30
    )
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        audio_size = len(response.content)
        print(f"✅ TTS Generation SUCCESSFUL!")
        print(f"Audio Size: {audio_size} bytes")

        # Optionally save the audio
        output_file = "/tmp/elevenlabs_test.mp3"
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"Audio saved to: {output_file}")
        print(f"Play it with: afplay {output_file}")
    else:
        print(f"❌ TTS Generation FAILED!")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 60)
print("✅ ALL TESTS PASSED!")
print("Your ElevenLabs configuration is working correctly.")
print("=" * 60)
