#!/usr/bin/env python3
"""
Simple gTTS test - check if Google TTS is working or rate-limited
"""
from gtts import gTTS
import tempfile
from pathlib import Path

print("🧪 Testing gTTS (unofficial Google TTS API)...")
print("=" * 60)

test_phrases = [
    ("Olá, como vai você?", "pt"),
    ("Bonjour, comment allez-vous?", "fr"),
]

for i, (text, lang) in enumerate(test_phrases, 1):
    print(f"\nTest {i}: {text} ({lang})")
    print("-" * 60)
    
    try:
        # Attempt to generate speech
        tts = gTTS(text=text, lang=lang, slow=False)
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            mp3_path = fp.name
            tts.save(mp3_path)
            
            # Check file size
            file_size = Path(mp3_path).stat().st_size
            print(f"✅ SUCCESS! Generated {file_size} bytes")
            
            # Clean up
            Path(mp3_path).unlink()
            
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}")
        print(f"   Error message: {str(e)[:200]}")
        
        # Check for specific error types
        if "429" in str(e) or "Too Many Requests" in str(e):
            print("   ⚠️  DIAGNOSIS: Rate limiting / IP blocking detected")
            print("   This is the same error seen in production!")
        elif "CAPTCHA" in str(e):
            print("   ⚠️  DIAGNOSIS: Google CAPTCHA challenge")
            print("   Google is blocking automated requests from this IP")
        elif "503" in str(e) or "Service Unavailable" in str(e):
            print("   ⚠️  DIAGNOSIS: Service temporarily unavailable")
        else:
            print("   ⚠️  DIAGNOSIS: Unknown error")

print("\n" + "=" * 60)
print("📊 Test Summary:")
print("- If all tests pass locally: gTTS works from your IP")
print("- If tests fail with 429: Your IP is rate-limited too")
print("- Compare with production logs to see if same error")
print("\n💡 Next steps:")
print("1. Check Streamlit Cloud logs for exact error message")
print("2. If 429 in logs: Google is blocking Streamlit Cloud IPs")
print("3. Solution: Must use Google Cloud TTS API (already implemented!)")
