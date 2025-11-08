#!/usr/bin/env python3
"""
streamlit_app_v2.py - Simplified Streamlit Web Interface for Brazilian Portuguese Pronunciation Practice

Run with: streamlit run streamlit_app_v2.py
"""

import streamlit as st
import json
import warnings
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import subprocess
import tempfile

# Suppress FP16 warning from Whisper on CPU
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")

try:
    import whisper
    import soundfile as sf
    import numpy as np
    from gtts import gTTS
except ImportError as e:
    st.error(f"Error: {e}")
    st.error("Please activate the virtual environment and install dependencies")
    st.stop()


# Page configuration
st.set_page_config(
    page_title="Portuguese Pronunciation Practice",
    page_icon="🇧🇷",
    layout="wide",
)


def load_settings():
    """Load user settings from config file"""
    config_file = Path("practice_config.json")
    default_settings = {
        "speed": 140,
        "pitch": 35,
        "voice": "pt-br",
        "model": "base",
        "duration": 3,
    }
    
    if config_file.exists():
        try:
            with open(config_file) as f:
                saved = json.load(f)
                default_settings.update(saved)
        except Exception:
            pass
    
    return default_settings


def save_settings(settings: Dict):
    """Save settings to config file"""
    try:
        with open("practice_config.json", 'w') as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        st.error(f"Could not save settings: {e}")


def load_history():
    """Load practice history"""
    history_file = Path("practice_history.json")
    if history_file.exists():
        try:
            with open(history_file) as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_history(history: List[Dict]):
    """Save practice history"""
    try:
        with open("practice_history.json", 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        st.error(f"Could not save history: {e}")


def initialize_session_state():
    """Initialize Streamlit session state"""
    if 'settings' not in st.session_state:
        st.session_state.settings = load_settings()
    
    if 'history' not in st.session_state:
        st.session_state.history = load_history()
    
    if 'current_session' not in st.session_state:
        st.session_state.current_session = {
            "date": datetime.now().isoformat(),
            "practices": []
        }
    
    if 'session_saved' not in st.session_state:
        st.session_state.session_saved = False
    
    if 'last_result' not in st.session_state:
        st.session_state.last_result = None
    
    if 'whisper_model' not in st.session_state:
        st.session_state.whisper_model = None
        st.session_state.whisper_model_name = None


def get_whisper_model(model_name: str):
    """Load or get cached Whisper model"""
    if st.session_state.whisper_model_name != model_name:
        with st.spinner(f"Loading Whisper model '{model_name}'..."):
            st.session_state.whisper_model = whisper.load_model(model_name)
            st.session_state.whisper_model_name = model_name
    return st.session_state.whisper_model


def get_espeak_path():
    """Get espeak-ng path (local build or system-wide)"""
    local_path = "./local/bin/run-espeak-ng"
    if Path(local_path).exists():
        return local_path
    # Try system-wide espeak-ng (for Streamlit Cloud)
    return "espeak-ng"


def get_phonemes(text: str, voice: str = "pt-br") -> str:
    """Get eSpeak phoneme codes (eIPA) for text"""
    try:
        result = subprocess.run(
            [get_espeak_path(), "-v", voice, "-x", "-q", text],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "[phonemes unavailable]"


def get_ipa(text: str, voice: str = "pt-br") -> str:
    """Get IPA transcription for text"""
    try:
        result = subprocess.run(
            [get_espeak_path(), "-v", voice, "--ipa", "-q", text],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "[IPA unavailable]"


def speak_text(text: str, voice: str = "pt-br", speed: int = 160, pitch: int = 40):
    """Speak Portuguese text using eSpeak (local only)"""
    try:
        subprocess.run([
            get_espeak_path(),
            "-v", voice,
            "-s", str(speed),
            "-p", str(pitch),
            text
        ], check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass  # Silently fail if espeak not available


def speak_text_gtts(text: str, lang: str = "pt-br") -> bytes:
    """
    Generate speech using Google TTS (higher quality than eSpeak)
    Returns audio bytes for playback in Streamlit
    """
    # Use 'pt' for Portuguese (gTTS auto-detects Brazilian vs European)
    # or 'pt-br' specifically for Brazilian Portuguese
    tts = gTTS(text=text, lang=lang.replace('-br', ''), slow=False)
    
    # Save to temporary file and read back
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
        tts.save(fp.name)
        with open(fp.name, 'rb') as audio_file:
            audio_bytes = audio_file.read()
        Path(fp.name).unlink()  # Clean up temp file
    
    return audio_bytes


def transcribe_audio(audio_file: str, model):
    """
    Transcribe audio to text using Whisper
    
    Note: No initial_prompt is used to avoid biasing the transcription.
    We force Portuguese language detection and use low temperature for consistency.
    CRITICAL: language="pt" should FORCE Portuguese, but Whisper can still drift.
    """
    result = model.transcribe(
        audio=audio_file,
        language="pt",  # Force Portuguese (ISO 639-1 code) - should be absolute
        task="transcribe",
        temperature=0.0,  # Deterministic output
        no_speech_threshold=0.6,  # Higher threshold to reject non-speech (like beeps)
        logprob_threshold=-1.0,   # Stricter on low-confidence segments
        condition_on_previous_text=False,  # Don't use context from previous segments
        word_timestamps=False,  # Disable word-level timestamps to reduce space insertion
        compression_ratio_threshold=2.4  # Default is 2.4, keep it strict
    )
    
    # Double-check detected language (Whisper should respect language="pt" but doesn't always)
    detected_lang = result.get("language", "unknown")
    if detected_lang != "pt":
        # Log warning but continue (the transcription might still be Portuguese)
        import warnings
        warnings.warn(f"Whisper detected language '{detected_lang}' instead of 'pt'")
    
    return result["text"].strip().lower()


def compare_phonemes(user_phonemes: str, correct_phonemes: str):
    """Compare user phonemes with correct phonemes"""
    exact_match = user_phonemes == correct_phonemes
    
    if len(correct_phonemes) == 0:
        similarity = 0.0
    else:
        matches = sum(
            1 for a, b in zip(user_phonemes, correct_phonemes)
            if a == b
        )
        similarity = matches / max(len(user_phonemes), len(correct_phonemes))
    
    return exact_match, similarity


def practice_word_from_audio(text: str, audio_bytes: bytes, settings: Dict):
    """
    Practice a word/phrase using pre-recorded audio
    
    Logic:
    1. Transcribe audio to text (with proper spacing)
    2. Generate phonemes for both target and recognized text (preserving word boundaries)
    3. For comparison: strip spaces from phonemes only (not from text)
    4. This allows flexible matching while maintaining proper IPA display
    """
    try:
        # Save audio bytes to temporary file
        temp_audio = "temp_streamlit_recording.wav"
        with open(temp_audio, 'wb') as f:
            f.write(audio_bytes)
        
        # Preprocess audio: trim silence/noise from start and end
        # This helps remove recording beeps and other artifacts
        try:
            audio_data, sample_rate = sf.read(temp_audio)
            
            # Simple energy-based trimming
            # Calculate short-term energy
            frame_length = int(0.02 * sample_rate)  # 20ms frames
            energy = np.array([
                np.sum(audio_data[i:i+frame_length]**2) 
                for i in range(0, len(audio_data) - frame_length, frame_length)
            ])
            
            # Find speech boundaries (energy > 1% of max energy)
            threshold = 0.01 * np.max(energy)
            speech_frames = np.where(energy > threshold)[0]
            
            if len(speech_frames) > 0:
                start_frame = max(0, speech_frames[0] - 2)  # Add 2 frames padding
                end_frame = min(len(energy), speech_frames[-1] + 3)
                
                start_sample = start_frame * frame_length
                end_sample = end_frame * frame_length
                
                trimmed_audio = audio_data[start_sample:end_sample]
                
                # Save trimmed audio
                sf.write(temp_audio, trimmed_audio, sample_rate)
        except Exception as e:
            # If trimming fails, continue with original audio
            pass
        
        # Get Whisper model
        model = get_whisper_model(settings['model'])
        
        # Get correct pronunciation
        correct_phonemes = get_phonemes(text, settings['voice'])
        correct_ipa = get_ipa(text, settings['voice'])
        
        # Transcribe user's audio
        recognized_text = transcribe_audio(temp_audio, model)
        
        # Get phonemes with proper spacing (for display)
        user_phonemes = get_phonemes(recognized_text, settings['voice'])
        user_ipa = get_ipa(recognized_text, settings['voice'])
        
        # For comparison: normalize by removing spaces from PHONEMES, not text
        # This allows flexible matching while preserving word boundaries in display
        correct_phonemes_normalized = correct_phonemes.replace(" ", "")
        user_phonemes_normalized = user_phonemes.replace(" ", "")
        
        # Compare normalized phonemes (without spaces)
        exact_match, similarity = compare_phonemes(user_phonemes_normalized, correct_phonemes_normalized)
        
        # Keep the original recording for playback
        # (Don't delete temp_audio - we'll save it in the result)
        
        result = {
            "target": text,
            "recognized": recognized_text,
            "correct_phonemes": correct_phonemes,
            "user_phonemes": user_phonemes,
            "correct_ipa": correct_ipa,
            "user_ipa": user_ipa,
            "exact_match": exact_match,
            "similarity": similarity,
            "user_audio_bytes": audio_bytes  # Save the original recording
        }
        
        # Save to current session
        st.session_state.current_session["practices"].append({
            "time": datetime.now().isoformat(),
            **result
        })
        st.session_state.session_saved = False
        st.session_state.last_result = result
        
        return result
        
    except Exception as e:
        st.error(f"Error during practice: {e}")
        import traceback
        st.error(traceback.format_exc())
        return None


def save_current_session():
    """Save current session to history"""
    if st.session_state.current_session["practices"]:
        st.session_state.history.append(st.session_state.current_session)
        save_history(st.session_state.history)
        
        # Reset current session
        st.session_state.current_session = {
            "date": datetime.now().isoformat(),
            "practices": []
        }
        st.session_state.session_saved = True
        st.success("✓ Session saved!")
    else:
        st.warning("No practices in current session to save")


def main():
    """Main Streamlit app"""
    initialize_session_state()
    
    # Header
    st.title("🇧🇷 Brazilian Portuguese Pronunciation Practice")
    st.markdown("---")
    
    # Sidebar - Settings and Navigation
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Voice settings
        st.session_state.settings['speed'] = st.slider(
            "Speed (wpm)", 80, 450, st.session_state.settings['speed'], 10,
            help="Lower = slower speech"
        )
        
        st.session_state.settings['pitch'] = st.slider(
            "Pitch", 0, 99, st.session_state.settings['pitch'], 5
        )
        
        st.session_state.settings['voice'] = st.selectbox(
            "Voice",
            ["pt-br", "pt"],
            index=0 if st.session_state.settings['voice'] == "pt-br" else 1,
            help="pt-br = Brazilian, pt = European"
        )
        
        st.session_state.settings['model'] = st.selectbox(
            "Whisper Model",
            ["tiny", "base", "small", "medium", "large"],
            index=["tiny", "base", "small", "medium", "large"].index(st.session_state.settings['model'])
        )
        
        if st.button("💾 Save Settings"):
            save_settings(st.session_state.settings)
            st.success("Settings saved!")
        
        st.markdown("---")
        
        # Session info
        st.header("📊 Current Session")
        practice_count = len(st.session_state.current_session["practices"])
        st.metric("Practices", practice_count)
        
        if practice_count > 0:
            perfect = sum(1 for p in st.session_state.current_session["practices"] if p.get("exact_match", False))
            st.metric("Perfect", f"{perfect}/{practice_count}")
            
            if not st.session_state.session_saved:
                st.warning(f"⚠️ {practice_count} unsaved practice(s)")
                if st.button("💾 Save Session Now"):
                    save_current_session()
    
    # Main content - Tabs
    tab1, tab2, tab3 = st.tabs([
        "🎯 Quick Practice",
        "📊 Statistics",
        "📜 History"
    ])
    
    # Tab 1: Quick Practice
    with tab1:
        st.header("Quick Practice")
        st.write("Practice a single word or phrase")
        
        text = st.text_input("Enter word or phrase:", key="practice_text")
        
        if text:
            # Listen First button
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("🔊 Listen First", key="listen_btn"):
                    with st.spinner("Generating audio..."):
                        audio_bytes = speak_text_gtts(text, st.session_state.settings['voice'])
                        st.audio(audio_bytes, format='audio/mp3')
            
            with col2:
                st.write("� Click to hear the target pronunciation before recording")
            
            st.markdown("---")
            st.write(" Now record your pronunciation:")
            st.info("💡 Wait for the recording beep to finish before speaking. The app will automatically trim silence and enforce Portuguese language detection.")
            
            # Streamlit's built-in audio input
            audio_data = st.audio_input("Click to record", key="audio_input")
            
            if audio_data:
                st.audio(audio_data)
                
                col1, col2 = st.columns([1, 3])
                with col1:
                    if st.button("✅ Check Pronunciation", key="submit_btn", type="primary"):
                        with st.spinner("Processing..."):
                            result = practice_word_from_audio(
                                text,
                                audio_data.getvalue(),
                                st.session_state.settings
                            )
                
                with col2:
                    if st.button("🔄 Clear Recording", key="clear_btn"):
                        # Clear the last result and reset
                        st.session_state.last_result = None
                        st.rerun()
        else:
            st.info("👆 Enter a word or phrase above to begin")
        
        # Show last result
        if st.session_state.last_result:
            st.markdown("---")
            st.header("Results")
            result = st.session_state.last_result
            
            if result["exact_match"]:
                st.success("🎉 PERFECT MATCH! Well done!")
            else:
                st.info(f"📊 Score: {result['similarity']:.1%}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Target")
                st.write(f"**Text:** {result['target']}")
                st.write(f"**eIPA:** {result['correct_phonemes']}")
                if result.get('correct_ipa'):
                    st.write(f"**IPA:** {result['correct_ipa']}")
                
                # Button to hear target again
                if st.button("🔊 Hear Target (Google TTS)", key="hear_target"):
                    audio_bytes = speak_text_gtts(result['target'], st.session_state.settings['voice'])
                    st.audio(audio_bytes, format='audio/mp3')
            
            with col2:
                st.subheader("Your Pronunciation")
                st.write(f"**Recognized:** {result['recognized']}")
                st.write(f"**eIPA:** {result['user_phonemes']}")
                if result.get('user_ipa'):
                    st.write(f"**IPA:** {result['user_ipa']}")
                
                # Show comparison note
                # Normalize text by removing punctuation for comparison
                import string
                target_clean = result['target'].lower().translate(str.maketrans('', '', string.punctuation))
                recognized_clean = result['recognized'].translate(str.maketrans('', '', string.punctuation))
                
                correct_phonemes_no_space = result['correct_phonemes'].replace(" ", "")
                user_phonemes_no_space = result['user_phonemes'].replace(" ", "")
                
                if correct_phonemes_no_space == user_phonemes_no_space and result['correct_phonemes'] != result['user_phonemes']:
                    st.success("✅ Phonemes match perfectly (spacing differences ignored)")
                elif target_clean != recognized_clean:
                    st.warning("⚠️ Different words recognized - try speaking more clearly")
                    
                    # Show character-by-character comparison for debugging
                    if st.checkbox("🔍 Show detailed comparison", key="show_detail"):
                        st.write("**Word comparison:**")
                        st.write(f"Target: `{target_clean}`")
                        st.write(f"Recognized: `{recognized_clean}`")
                        st.write("**Phoneme comparison (no spaces):**")
                        st.write(f"Target: `{correct_phonemes_no_space}`")
                        st.write(f"Yours: `{user_phonemes_no_space}`")
                        
                        # Show where they differ
                        min_len = min(len(correct_phonemes_no_space), len(user_phonemes_no_space))
                        diffs = []
                        for i in range(min_len):
                            if correct_phonemes_no_space[i] != user_phonemes_no_space[i]:
                                diffs.append(f"Position {i}: expected `{correct_phonemes_no_space[i]}`, got `{user_phonemes_no_space[i]}`")
                        if len(correct_phonemes_no_space) != len(user_phonemes_no_space):
                            diffs.append(f"Length: expected {len(correct_phonemes_no_space)}, got {len(user_phonemes_no_space)}")
                        if diffs:
                            st.write("**Differences:**")
                            for diff in diffs:
                                st.write(f"- {diff}")
                
                # Button to play back your actual recording
                if result.get('user_audio_bytes'):
                    if st.button("🔊 Hear Your Recording", key="hear_recording"):
                        st.audio(result['user_audio_bytes'], format='audio/wav')
                
                # Button to hear TTS of what was recognized (for comparison)
                if result['recognized'] != result['target']:
                    if st.button("🔊 Hear Recognized Text (TTS)", key="hear_recognized"):
                        audio_bytes = speak_text_gtts(result['recognized'], st.session_state.settings['voice'])
                        st.audio(audio_bytes, format='audio/mp3')
            
            # Optional: Hear eSpeak phoneme pronunciation
            if not result["exact_match"]:
                st.markdown("---")
                st.subheader("Compare Phoneme Sounds (eSpeak)")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔊 Correct Phonemes", key="phoneme_correct"):
                        speak_text(result['target'], 
                                 voice=st.session_state.settings['voice'],
                                 speed=st.session_state.settings['speed'],
                                 pitch=st.session_state.settings['pitch'])
                with col2:
                    if st.button("🔊 Your Phonemes", key="phoneme_yours"):
                        speak_text(result['recognized'],
                                 voice=st.session_state.settings['voice'],
                                 speed=st.session_state.settings['speed'],
                                 pitch=st.session_state.settings['pitch'])
    
    # Tab 2: Statistics
    with tab2:
        st.header("📊 Practice Statistics")
        
        # Current session stats
        if st.session_state.current_session["practices"]:
            st.subheader("🔵 Current Session")
            practices = st.session_state.current_session["practices"]
            perfect = sum(1 for p in practices if p.get("exact_match", False))
            avg_sim = sum(p["similarity"] for p in practices) / len(practices)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Practices", len(practices))
            col2.metric("Perfect", f"{perfect} ({perfect/len(practices):.1%})")
            col3.metric("Avg Similarity", f"{avg_sim:.1%}")
        
        # Overall stats
        if st.session_state.history:
            st.subheader("📈 All Time")
            
            total_practices = sum(len(s["practices"]) for s in st.session_state.history)
            total_perfect = sum(
                sum(1 for p in s["practices"] if p.get("match", False))
                for s in st.session_state.history
            )
            
            all_similarities = [
                p["similarity"]
                for s in st.session_state.history
                for p in s["practices"]
                if "similarity" in p
            ]
            
            if all_similarities:
                avg_all = sum(all_similarities) / len(all_similarities)
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Practices", total_practices)
                col2.metric("Total Perfect", f"{total_perfect} ({total_perfect/total_practices:.1%})")
                col3.metric("Overall Avg", f"{avg_all:.1%}")
                col4.metric("Sessions", len(st.session_state.history))
        else:
            st.info("No practice history yet. Start practicing!")
    
    # Tab 3: History
    with tab3:
        st.header("📜 Session History")
        
        if not st.session_state.history:
            st.info("No previous sessions")
        else:
            for i, session in enumerate(reversed(st.session_state.history[-10:]), 1):
                date = session["date"][:10]
                count = len(session["practices"])
                perfect = sum(1 for p in session["practices"] if p.get("match", False))
                
                with st.expander(f"{date} - {count} practices ({perfect} perfect)"):
                    for j, practice in enumerate(session["practices"], 1):
                        status = "✅" if practice.get("match", False) else f"📊 {practice.get('similarity', 0):.1%}"
                        
                        st.markdown(f"**{j}. {status}**")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("Target:", practice.get('target', 'N/A'))
                            if "correct_phonemes" in practice:
                                st.write("Correct eIPA:", practice['correct_phonemes'])
                        
                        with col2:
                            st.write("Recognized:", practice.get('recognized', 'N/A'))
                            if "user_phonemes" in practice:
                                st.write("Your eIPA:", practice['user_phonemes'])
                        
                        st.markdown("---")


if __name__ == "__main__":
    main()
