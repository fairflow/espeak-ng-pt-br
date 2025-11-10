#!/usr/bin/env python3
"""
Test audio generation to debug iOS playback issues.
This creates both MP3 and WAV files and tests them in Streamlit.
"""

import streamlit as st
from gtts import gTTS
import tempfile
import subprocess
from pathlib import Path

st.title("🔊 Audio Format Test")

test_text = st.text_input("Test phrase:", value="Olá, bom dia")

if st.button("Generate Audio") and test_text:
    
    # Generate MP3
    st.subheader("1. Generate MP3 with gTTS")
    with st.spinner("Generating MP3..."):
        tts = gTTS(text=test_text, lang='pt', slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as mp3_fp:
            mp3_path = mp3_fp.name
            tts.save(mp3_path)
            
            with open(mp3_path, 'rb') as f:
                mp3_bytes = f.read()
            
            st.success(f"✓ MP3 generated: {len(mp3_bytes)} bytes")
            st.write(f"Path: {mp3_path}")
    
    # Test MP3 playback
    st.subheader("2. Test MP3 Playback")
    st.audio(mp3_bytes, format='audio/mp3')
    
    # Convert to WAV
    st.subheader("3. Convert MP3 → WAV with ffmpeg")
    st.write("Converting... (no spinner to avoid deadlock)")
    
    wav_path = mp3_path.replace('.mp3', '.wav')
    
    # Run ffmpeg WITHOUT spinner - spinner + subprocess causes deadlock!
    result = subprocess.run(
        ['ffmpeg', '-i', mp3_path, '-acodec', 'pcm_s16le', 
         '-ar', '22050', '-y', wav_path],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        with open(wav_path, 'rb') as f:
            wav_bytes = f.read()
        st.success(f"✓ Converted to WAV: {len(wav_bytes)} bytes")
        st.audio(wav_bytes, format='audio/wav')
    else:
        st.error(f"Conversion failed: {result.stderr}")    # Test WAV playback
    if result.returncode == 0:
        st.subheader("4. Test WAV Playback")
        st.audio(wav_bytes, format='audio/wav')
    
    # Cleanup
    st.subheader("5. Cleanup")
    try:
        Path(mp3_path).unlink()
        if result.returncode == 0:
            Path(wav_path).unlink()
        st.success("✓ Temp files cleaned up")
    except Exception as e:
        st.warning(f"Cleanup warning: {e}")

st.markdown("---")
st.info("""
**Test Instructions:**
1. Enter a Portuguese phrase
2. Click "Generate Audio"
3. Try playing both MP3 and WAV
4. Check which format works on your device

**Expected behavior:**
- MP3 should work on desktop/macOS
- WAV should work everywhere including iOS Safari
""")
