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
        "comparison_algorithm": "edit_distance",  # or "positional"
        "asr_engine": "whisper",  # "whisper" or "wav2vec2"
        "whisper_model_size": "base",  # tiny, base, small, medium, large
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
    
    if 'wav2vec2_processor' not in st.session_state:
        st.session_state.wav2vec2_processor = None
        st.session_state.wav2vec2_model = None


def get_whisper_model(model_name: str):
    """Load or get cached Whisper model"""
    if st.session_state.whisper_model_name != model_name:
        with st.spinner(f"Loading Whisper model '{model_name}'..."):
            st.session_state.whisper_model = whisper.load_model(model_name)
            st.session_state.whisper_model_name = model_name
    return st.session_state.whisper_model


def get_wav2vec2_model():
    """Load or get cached wav2vec2 Portuguese model"""
    if 'wav2vec2_processor' not in st.session_state or st.session_state.wav2vec2_processor is None:
        try:
            with st.spinner("Loading wav2vec2 Portuguese model (first time may take a few minutes)..."):
                from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
                model_name = "jonatasgrosman/wav2vec2-large-xlsr-53-portuguese"
                st.session_state.wav2vec2_processor = Wav2Vec2Processor.from_pretrained(model_name)
                st.session_state.wav2vec2_model = Wav2Vec2ForCTC.from_pretrained(model_name)
        except ImportError:
            st.error("wav2vec2 requires 'transformers' and 'torch'. Install with: pip install transformers torch")
            return None, None
        except Exception as e:
            st.error(f"Failed to load wav2vec2 model: {e}")
            return None, None
    return st.session_state.wav2vec2_processor, st.session_state.wav2vec2_model


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


def transcribe_audio_whisper(audio_file: str, model):
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


def transcribe_audio_wav2vec2(audio_file: str, processor, model):
    """
    Transcribe audio to text using wav2vec2 Portuguese model
    """
    try:
        import torch
        import soundfile as sf
        
        # Load audio
        speech, sample_rate = sf.read(audio_file)
        
        # Resample if needed (wav2vec2 expects 16kHz)
        if sample_rate != 16000:
            import librosa
            speech = librosa.resample(speech, orig_sr=sample_rate, target_sr=16000)
        
        # Process
        inputs = processor(speech, sampling_rate=16000, return_tensors="pt", padding=True)
        
        with torch.no_grad():
            logits = model(inputs.input_values).logits
        
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = processor.batch_decode(predicted_ids)[0]
        
        return transcription.strip().lower()
        
    except Exception as e:
        st.error(f"wav2vec2 transcription failed: {e}")
        return ""


def transcribe_audio(audio_file: str, settings: Dict):
    """
    Transcribe audio using the selected ASR engine
    """
    asr_engine = settings.get('asr_engine', 'whisper')
    
    if asr_engine == 'wav2vec2':
        processor, model = get_wav2vec2_model()
        if processor is None or model is None:
            st.warning("wav2vec2 unavailable, falling back to Whisper")
            asr_engine = 'whisper'
        else:
            return transcribe_audio_wav2vec2(audio_file, processor, model)
    
    # Default to Whisper
    model_size = settings.get('whisper_model_size', 'base')
    model = get_whisper_model(model_size)
    return transcribe_audio_whisper(audio_file, model)


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate Levenshtein (edit) distance between two strings.
    Returns the minimum number of single-character edits (insertions, deletions, substitutions).
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # Cost of insertions, deletions, or substitutions
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def get_edit_operations(s1: str, s2: str):
    """
    Get the actual edit operations needed to transform s1 into s2.
    Returns a list of tuples: (operation, position, char1, char2)
    where operation is 'match', 'substitute', 'insert', or 'delete'
    """
    # Build the DP table
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(
                    dp[i-1][j],    # delete
                    dp[i][j-1],    # insert
                    dp[i-1][j-1]   # substitute
                )
    
    # Backtrack to find operations
    operations = []
    i, j = m, n
    while i > 0 or j > 0:
        if i > 0 and j > 0 and s1[i-1] == s2[j-1]:
            operations.append(('match', i-1, s1[i-1], s2[j-1]))
            i -= 1
            j -= 1
        elif i > 0 and j > 0 and dp[i][j] == dp[i-1][j-1] + 1:
            operations.append(('substitute', i-1, s1[i-1], s2[j-1]))
            i -= 1
            j -= 1
        elif j > 0 and dp[i][j] == dp[i][j-1] + 1:
            operations.append(('insert', i, '-', s2[j-1]))
            j -= 1
        elif i > 0 and dp[i][j] == dp[i-1][j] + 1:
            operations.append(('delete', i-1, s1[i-1], '-'))
            i -= 1
    
    operations.reverse()
    return operations


def compare_phonemes_positional(user_phonemes: str, correct_phonemes: str):
    """
    DEPRECATED: Simple positional matching (fails with insertions/deletions).
    Kept for reference but not recommended for use.
    """
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


def compare_phonemes_edit_distance(user_phonemes: str, correct_phonemes: str):
    """
    Compare phonemes using edit distance (Levenshtein).
    Handles insertions, deletions, and substitutions gracefully.
    
    Returns:
        exact_match: bool - True if strings are identical
        similarity: float - 0.0 to 1.0, where 1.0 is perfect match
        distance: int - Number of edits needed
    """
    exact_match = user_phonemes == correct_phonemes
    
    if len(correct_phonemes) == 0:
        return exact_match, 0.0, len(user_phonemes)
    
    distance = levenshtein_distance(user_phonemes, correct_phonemes)
    max_length = max(len(user_phonemes), len(correct_phonemes))
    
    # Similarity: 1.0 means perfect match, 0.0 means completely different
    similarity = 1.0 - (distance / max_length)
    
    return exact_match, similarity, distance


def compare_phonemes(user_phonemes: str, correct_phonemes: str, algorithm: str = "edit_distance"):
    """
    Modular phoneme comparison with selectable algorithms.
    
    Args:
        user_phonemes: Phonemes from user's speech
        correct_phonemes: Target phonemes
        algorithm: "edit_distance" (default) or "positional"
    
    Returns:
        exact_match: bool
        similarity: float (0.0 to 1.0)
        distance: int (only for edit_distance, None otherwise)
    """
    if algorithm == "edit_distance":
        return compare_phonemes_edit_distance(user_phonemes, correct_phonemes)
    elif algorithm == "positional":
        exact_match, similarity = compare_phonemes_positional(user_phonemes, correct_phonemes)
        return exact_match, similarity, None
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")


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
        
        # Get correct pronunciation
        correct_phonemes = get_phonemes(text, settings['voice'])
        correct_ipa = get_ipa(text, settings['voice'])
        
        # Transcribe user's audio using selected ASR engine
        recognized_text = transcribe_audio(temp_audio, settings)
        
        # Get phonemes with proper spacing (for display)
        user_phonemes = get_phonemes(recognized_text, settings['voice'])
        user_ipa = get_ipa(recognized_text, settings['voice'])
        
        # For comparison: normalize by removing spaces from PHONEMES, not text
        # This allows flexible matching while preserving word boundaries in display
        correct_phonemes_normalized = correct_phonemes.replace(" ", "")
        user_phonemes_normalized = user_phonemes.replace(" ", "")
        
        # Compare normalized phonemes (without spaces) using edit distance
        # Get algorithm from settings (default: edit_distance)
        algorithm = settings.get('comparison_algorithm', 'edit_distance')
        exact_match, similarity, edit_distance = compare_phonemes(
            user_phonemes_normalized, 
            correct_phonemes_normalized,
            algorithm=algorithm
        )
        
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
            "edit_distance": edit_distance,
            "correct_phonemes_normalized": correct_phonemes_normalized,
            "user_phonemes_normalized": user_phonemes_normalized,
            "user_audio_bytes": audio_bytes  # Keep in session for playback, but don't save to JSON
        }
        
        # Save to current session (exclude bytes for JSON serialization)
        session_data = {k: v for k, v in result.items() if k != "user_audio_bytes"}
        st.session_state.current_session["practices"].append({
            "time": datetime.now().isoformat(),
            **session_data
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
        
        st.markdown("**🎙️ Speech Recognition**")
        
        st.session_state.settings['asr_engine'] = st.selectbox(
            "ASR Engine",
            ["whisper", "wav2vec2"],
            index=0 if st.session_state.settings.get('asr_engine', 'whisper') == 'whisper' else 1,
            help="whisper: Multilingual (99 languages)\nwav2vec2: Portuguese-specific (may be more accurate)"
        )
        
        # Only show Whisper model size if Whisper is selected
        if st.session_state.settings['asr_engine'] == 'whisper':
            st.session_state.settings['whisper_model_size'] = st.selectbox(
                "Whisper Model Size",
                ["tiny", "base", "small", "medium", "large"],
                index=["tiny", "base", "small", "medium", "large"].index(
                    st.session_state.settings.get('whisper_model_size', 'base')
                ),
                help="Larger = more accurate but slower. tiny is fastest, large is most accurate."
            )
            # Keep 'model' in sync for backwards compatibility
            st.session_state.settings['model'] = st.session_state.settings['whisper_model_size']
        else:
            st.caption("Using wav2vec2-large-xlsr-53-portuguese")
        
        st.session_state.settings['comparison_algorithm'] = st.selectbox(
            "Scoring Algorithm",
            ["edit_distance", "positional"],
            index=0 if st.session_state.settings.get('comparison_algorithm', 'edit_distance') == 'edit_distance' else 1,
            help="edit_distance: Handles insertions/deletions (recommended)\npositional: Simple character-by-character matching"
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
                score_col1, score_col2 = st.columns([2, 1])
                with score_col1:
                    st.info(f"📊 Score: {result['similarity']:.1%}")
                with score_col2:
                    if result.get('edit_distance') is not None:
                        st.metric("Edit Distance", result['edit_distance'],
                                help="Number of edits needed to match target")
            
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
                
                # Only show messages if there are meaningful differences
                phonemes_match = correct_phonemes_no_space == user_phonemes_no_space
                text_matches = target_clean == recognized_clean
                score_is_high = result['similarity'] >= 0.95
                
                if phonemes_match and result['correct_phonemes'] != result['user_phonemes']:
                    st.success("✅ Phonemes match perfectly (spacing differences ignored)")
                elif not text_matches and not score_is_high:
                    # Only warn if BOTH text differs AND score is low
                    st.warning("⚠️ Different words recognized - try speaking more clearly")
                elif score_is_high and not text_matches:
                    # High score but text differs (e.g., punctuation) - show positive message
                    st.info("ℹ️ Excellent pronunciation! (Minor text differences ignored)")
                
                # Show detailed phoneme analysis (works with edit distance!)
                if st.checkbox("🔍 Show detailed phoneme analysis", key="show_detail"):
                    st.markdown("#### Phoneme Analysis")
                    st.write(f"**Algorithm:** {st.session_state.settings.get('comparison_algorithm', 'edit_distance')}")
                    
                    if result.get('edit_distance') is not None:
                        st.write(f"**Edit Distance:** {result['edit_distance']} edit(s) needed")
                    
                    st.write("**Normalized phonemes (spaces removed for comparison):**")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.code(result.get('correct_phonemes_normalized', correct_phonemes_no_space), language=None)
                        st.caption(f"Target ({len(result.get('correct_phonemes_normalized', correct_phonemes_no_space))} chars)")
                    with col_b:
                        st.code(result.get('user_phonemes_normalized', user_phonemes_no_space), language=None)
                        st.caption(f"Yours ({len(result.get('user_phonemes_normalized', user_phonemes_no_space))} chars)")
                    
                    # Visual comparison
                    target_norm = result.get('correct_phonemes_normalized', correct_phonemes_no_space)
                    user_norm = result.get('user_phonemes_normalized', user_phonemes_no_space)
                    
                    if target_norm == user_norm:
                        st.success("🎯 Phonemes are identical!")
                    else:
                        # Use edit distance operations for accurate difference analysis
                        operations = get_edit_operations(target_norm, user_norm)
                        
                        # Count operation types
                        matches = sum(1 for op in operations if op[0] == 'match')
                        substitutions = [op for op in operations if op[0] == 'substitute']
                        insertions = [op for op in operations if op[0] == 'insert']
                        deletions = [op for op in operations if op[0] == 'delete']
                        
                        st.info(f"📊 {matches} matches, {len(substitutions)} substitutions, {len(insertions)} insertions, {len(deletions)} deletions")
                        
                        # Show the actual differences (limit to first 5 non-matches)
                        diffs = []
                        for op_type, pos, c1, c2 in operations:
                            if op_type == 'substitute':
                                diffs.append(f"Position {pos}: `{c1}` → `{c2}` (substitute)")
                            elif op_type == 'insert':
                                diffs.append(f"Position {pos}: inserted `{c2}`")
                            elif op_type == 'delete':
                                diffs.append(f"Position {pos}: deleted `{c1}`")
                            
                            if len(diffs) >= 5:
                                break
                        
                        if diffs:
                            st.write("**Key differences (first 5):**")
                            for diff in diffs:
                                st.write(f"• {diff}")
                        
                        if len(substitutions) + len(insertions) + len(deletions) > 5:
                            st.caption(f"... and {len(substitutions) + len(insertions) + len(deletions) - 5} more differences")
                
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
