#!/usr/bin/env python3
"""
Portuguese Pronunciation Trainer - Web Application

Streamlit-based app for practicing Brazilian Portuguese pronunciation
with real-time feedback using speech recognition and phonetic analysis.

Run with: streamlit run app.py
"""

__version__ = "1.0.0"
__app_name__ = "Pronunciation Trainer"
__author__ = "Matthew & Contributors"
__license__ = "GPL-3.0"

# Language configuration
LANGUAGE_CONFIG = {
    "Portuguese": {
        "code": "pt",
        "whisper_code": "pt",
        "display_name": "Portuguese Pronunciation Trainer",
        "voices": {
            "gtts": ["pt-br", "pt"],
            "espeak": ["pt-br", "pt"]
        }
    },
    "Dutch": {
        "code": "nl",
        "whisper_code": "nl",
        "display_name": "Dutch/Flemish Pronunciation Trainer",
        "voices": {
            "gtts": ["nl"],
            "espeak": ["nl"]
        }
    },
    "French": {
        "code": "fr",
        "whisper_code": "fr",
        "display_name": "French Pronunciation Trainer",
        "voices": {
            "gtts": ["fr"],
            "espeak": ["fr-fr"]
        }
    }
}

# Version History:
# 1.0.0 (2025-11-11):
#   - Add multi-language support (Portuguese, French, Dutch, Flemish)
#   - Language-specific session tracking
#   - Dynamic app title based on selected language
#   - Language selector in sidebar
# 0.9.3 (2025-11-11):
#   - Improve audio trimming with 200ms padding (prevents speech artifacts)
#   - Show trimmed audio in results (what was actually recognized)
#   - Use IPA instead of eIPA for normalized phonemes display (user-friendly)
#   - Fix Edit button UX: grayed out in edit mode, clear "Return to Guided Mode" button
#   - British spelling: "Normalised" in UI
# 0.9.2 (2025-11-10):
#   - Add TTS engine selection (Google TTS vs eSpeak)
#   - Fix speed/pitch settings now work (with eSpeak)
#   - Add slow mode for Google TTS (simple on/off)
#   - Add documentation links in sidebar
#   - Reorganize documentation (USER_GUIDE, TESTING_GUIDE, DEVELOPER_GUIDE)
# 0.9.1 (2025-11-10):
#   - Fix WAV audio setting not persisting when saved
# 0.9.0 (2025-11-10):
#   - Add iOS Safari audio compatibility (WAV conversion)
#   - Fix audio generation deadlock with subprocess.DEVNULL
#   - Add user-adjustable silence trimming threshold
#   - Improve CCS testing framework integration
#   - Implement edit distance scoring algorithm
#   - Add version management system

import streamlit as st
import json
import warnings
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import subprocess
import tempfile
import os

# Environment configuration
IS_LOCAL_DEV = os.path.exists('./local/bin/run-espeak-ng')  # True if local eSpeak build exists

# Suppress warnings
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")  # Whisper on CPU
warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL")  # LibreSSL compatibility

try:
    import whisper
    import soundfile as sf
    import numpy as np
    from gtts import gTTS
except ImportError as e:
    st.error(f"Error: {e}")
    st.error("Please activate the virtual environment and install dependencies")
    st.stop()

# CCS Testing Framework (optional)
try:
    from ccs_test_integration import CCSTestSession
    CCS_AVAILABLE = True
except ImportError:
    CCS_AVAILABLE = False


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
        "silence_threshold": 0.01,  # Energy threshold for silence detection (0.001-0.1)
        "use_wav_audio": False,  # Convert TTS audio to WAV for iOS Safari compatibility
        "tts_engine": "gtts",  # "gtts" (Google TTS, high quality) or "espeak" (adjustable speed/pitch)
        "gtts_slow": False,  # Enable slow speech for Google TTS (when tts_engine='gtts')
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
    
    # Initialize language selection (default to Portuguese)
    if 'language' not in st.session_state:
        st.session_state.language = "Portuguese"
    
    if 'history' not in st.session_state:
        st.session_state.history = load_history()
    
    # Language-specific session tracking
    if 'current_sessions' not in st.session_state:
        st.session_state.current_sessions = {}
    
    # Get or create current session for selected language
    if st.session_state.language not in st.session_state.current_sessions:
        st.session_state.current_sessions[st.session_state.language] = {
            "date": datetime.now().isoformat(),
            "practices": []
        }
    
    if 'session_saved' not in st.session_state:
        st.session_state.session_saved = False
    
    if 'last_result' not in st.session_state:
        st.session_state.last_result = None
    
    if 'audio_input_key' not in st.session_state:
        st.session_state.audio_input_key = 0
    
    if 'whisper_model' not in st.session_state:
        st.session_state.whisper_model = None
        st.session_state.whisper_model_name = None
    
    if 'wav2vec2_processor' not in st.session_state:
        st.session_state.wav2vec2_processor = None
        st.session_state.wav2vec2_model = None
    
    # CCS Testing Framework initialization (disabled by default)
    if CCS_AVAILABLE and 'ccs_test' not in st.session_state:
        st.session_state.ccs_test = CCSTestSession(enabled=False)


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


def speak_text_gtts(text: str, lang: str = "pt-br", use_wav: bool = False, slow: bool = False) -> tuple[bytes, str]:
    """
    Generate speech using Google TTS (higher quality than eSpeak)
    Returns tuple of (audio_bytes, format) for playback in Streamlit
    
    Args:
        text: Text to speak
        lang: Language code (default pt-br)
        use_wav: If True, convert MP3 to WAV for iOS Safari compatibility
        slow: If True, speak at ~50% speed (Google TTS slow mode)
        
    Returns:
        (audio_bytes, format) where format is 'audio/mp3' or 'audio/wav'
    """
    # Use 'pt' for Portuguese (gTTS auto-detects Brazilian vs European)
    # or 'pt-br' specifically for Brazilian Portuguese
    tts = gTTS(text=text, lang=lang.replace('-br', ''), slow=slow)
    
    # Save to temporary file and read back
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
        mp3_path = fp.name
        tts.save(mp3_path)
        
        if use_wav:
            # Convert MP3 to WAV for iOS Safari compatibility
            wav_path = mp3_path.replace('.mp3', '.wav')
            
            # Run ffmpeg without capturing output to avoid pipe buffer deadlock
            result = subprocess.run(
                ['ffmpeg', '-i', mp3_path, '-acodec', 'pcm_s16le', 
                 '-ar', '22050', '-y', wav_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            if result.returncode == 0:
                with open(wav_path, 'rb') as audio_file:
                    audio_bytes = audio_file.read()
                Path(wav_path).unlink()  # Clean up WAV
                Path(mp3_path).unlink()  # Clean up MP3
                return audio_bytes, 'audio/wav'
            else:
                # Conversion failed, fall back to MP3
                with open(mp3_path, 'rb') as audio_file:
                    audio_bytes = audio_file.read()
                Path(mp3_path).unlink()
                return audio_bytes, 'audio/mp3'
        else:
            # Return MP3
            with open(mp3_path, 'rb') as audio_file:
                audio_bytes = audio_file.read()
            Path(mp3_path).unlink()  # Clean up temp file
            return audio_bytes, 'audio/mp3'


def generate_target_audio(text: str, settings: Dict) -> tuple[bytes, str]:
    """
    Generate target pronunciation audio using the configured TTS engine
    
    Args:
        text: Text to speak
        settings: User settings dict containing tts_engine, voice, speed, pitch, use_wav_audio
        
    Returns:
        (audio_bytes, format) where format is 'audio/mp3', 'audio/wav', or 'audio/x-wav'
    """
    tts_engine = settings.get('tts_engine', 'gtts')
    
    if tts_engine == 'espeak':
        # Use eSpeak with speed and pitch control
        audio_bytes = speak_text(
            text,
            voice=settings.get('voice', 'pt-br'),
            speed=settings.get('speed', 140),
            pitch=settings.get('pitch', 35)
        )
        return audio_bytes, 'audio/x-wav'
    else:
        # Use Google TTS (default, high quality)
        return speak_text_gtts(
            text,
            lang=settings.get('voice', 'pt-br'),
            use_wav=settings.get('use_wav_audio', False),
            slow=settings.get('gtts_slow', False)
        )


def transcribe_audio_whisper(audio_file: str, model, language_code: str = "pt"):
    """
    Transcribe audio to text using Whisper
    
    Args:
        audio_file: Path to audio file
        model: Whisper model instance
        language_code: Whisper language code (e.g., 'pt', 'fr', 'nl')
    
    Note: No initial_prompt is used to avoid biasing the transcription.
    We force language detection and use low temperature for consistency.
    """
    result = model.transcribe(
        audio=audio_file,
        language=language_code,  # Force language (ISO 639-1 code)
        task="transcribe",
        temperature=0.0,  # Deterministic output
        no_speech_threshold=0.6,  # Higher threshold to reject non-speech (like beeps)
        logprob_threshold=-1.0,   # Stricter on low-confidence segments
        condition_on_previous_text=False,  # Don't use context from previous segments
        word_timestamps=False,  # Disable word-level timestamps to reduce space insertion
        compression_ratio_threshold=2.4  # Default is 2.4, keep it strict
    )
    
    # Double-check detected language (Whisper should respect language parameter but doesn't always)
    detected_lang = result.get("language", "unknown")
    if detected_lang != language_code:
        # Log warning but continue (the transcription might still be correct)
        import warnings
        warnings.warn(f"Whisper detected language '{detected_lang}' instead of '{language_code}'")
    
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


def transcribe_audio(audio_file: str, settings: Dict, language: str = "Portuguese"):
    """
    Transcribe audio using the selected ASR engine
    
    Args:
        audio_file: Path to audio file
        settings: App settings dict
        language: Selected language name (e.g., "Portuguese", "French")
    """
    asr_engine = settings.get('asr_engine', 'whisper')
    
    # Get language configuration
    lang_config = LANGUAGE_CONFIG[language]
    whisper_code = lang_config['whisper_code']
    
    if asr_engine == 'wav2vec2':
        # wav2vec2 is Portuguese-only
        if whisper_code != 'pt':
            st.warning("wav2vec2 only supports Portuguese, falling back to Whisper")
            asr_engine = 'whisper'
        else:
            processor, model = get_wav2vec2_model()
            if processor is None or model is None:
                st.warning("wav2vec2 unavailable, falling back to Whisper")
                asr_engine = 'whisper'
            else:
                return transcribe_audio_wav2vec2(audio_file, processor, model)
    
    # Default to Whisper
    model_size = settings.get('whisper_model_size', 'base')
    model = get_whisper_model(model_size)
    return transcribe_audio_whisper(audio_file, model, whisper_code)


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
        # This helps remove system noise and other artifacts
        try:
            audio_data, sample_rate = sf.read(temp_audio)
            
            # Simple energy-based trimming
            # Calculate short-term energy
            frame_length = int(0.02 * sample_rate)  # 20ms frames
            energy = np.array([
                np.sum(audio_data[i:i+frame_length]**2) 
                for i in range(0, len(audio_data) - frame_length, frame_length)
            ])
            
            # Find speech boundaries using user-configurable threshold
            # threshold is a percentage of max energy (default 0.01 = 1%)
            silence_threshold = settings.get('silence_threshold', 0.01)
            threshold = silence_threshold * np.max(energy)
            speech_frames = np.where(energy > threshold)[0]
            
            if len(speech_frames) > 0:
                # Add 200ms padding before and after to avoid speech artifacts
                padding_ms = 0.2  # 200ms as requested
                padding_samples = int(padding_ms * sample_rate)
                
                start_sample = max(0, speech_frames[0] * frame_length - padding_samples)
                end_sample = min(len(audio_data), (speech_frames[-1] + 1) * frame_length + padding_samples)
                
                trimmed_audio = audio_data[start_sample:end_sample]
                
                # Save trimmed audio
                sf.write(temp_audio, trimmed_audio, sample_rate)
                
                # Also save trimmed audio bytes for playback
                import io
                trimmed_buffer = io.BytesIO()
                sf.write(trimmed_buffer, trimmed_audio, sample_rate, format='WAV')
                trimmed_audio_bytes = trimmed_buffer.getvalue()
            else:
                trimmed_audio_bytes = audio_bytes
        except Exception as e:
            # If trimming fails, continue with original audio
            pass
        
        # Get correct pronunciation
        correct_phonemes = get_phonemes(text, settings['voice'])
        correct_ipa = get_ipa(text, settings['voice'])
        
        # Transcribe user's audio using selected ASR engine
        recognized_text = transcribe_audio(temp_audio, settings, st.session_state.language)
        
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
            "user_audio_bytes": audio_bytes,  # Original recording
            "user_audio_trimmed_bytes": trimmed_audio_bytes  # Trimmed version (what was actually recognized)
        }
        
        # Save to current session (exclude bytes for JSON serialization)
        session_data = {k: v for k, v in result.items() if k not in ["user_audio_bytes", "user_audio_trimmed_bytes"]}
        st.session_state.current_sessions[st.session_state.language]["practices"].append({
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
    current_session = st.session_state.current_sessions[st.session_state.language]
    if current_session["practices"]:
        st.session_state.history.append(current_session)
        save_history(st.session_state.history)
        
        # Reset current session for this language
        st.session_state.current_sessions[st.session_state.language] = {
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
    
    # Header - Dynamic title based on selected language
    lang_config = LANGUAGE_CONFIG[st.session_state.language]
    
    # Add flag emoji for each language
    flag_emojis = {
        "Portuguese": "🇧🇷",
        "French": "🇫🇷",
        "Dutch": "🇳🇱",
        "Flemish": "🇧🇪"
    }
    
    flag = flag_emojis.get(st.session_state.language, "🌍")
    st.title(f"{flag} {lang_config['display_name']}")
    st.markdown("---")
    
    # Sidebar - Settings and Navigation
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Language selection
        st.markdown("**🌍 Language**")
        
        previous_language = st.session_state.language
        st.session_state.language = st.selectbox(
            "Training Language",
            list(LANGUAGE_CONFIG.keys()),
            index=list(LANGUAGE_CONFIG.keys()).index(st.session_state.language),
            help="Select the language you want to practice"
        )
        
        # If language changed, ensure session exists for new language
        if previous_language != st.session_state.language:
            if st.session_state.language not in st.session_state.current_sessions:
                st.session_state.current_sessions[st.session_state.language] = {
                    "date": datetime.now().isoformat(),
                    "practices": []
                }
        
        # Get current language config
        lang_config = LANGUAGE_CONFIG[st.session_state.language]
        
        # TTS Engine selection
        st.markdown("**🔊 Text-to-Speech Engine**")
        
        st.session_state.settings['tts_engine'] = st.selectbox(
            "TTS Engine",
            ["gtts", "espeak"],
            index=0 if st.session_state.settings.get('tts_engine', 'gtts') == 'gtts' else 1,
            help="gtts: Google TTS (high quality, limited speed control)\nespeak: eSpeak (adjustable speed/pitch, robotic voice)"
        )
        
        tts_is_espeak = st.session_state.settings.get('tts_engine', 'gtts') == 'espeak'
        
        # Voice settings
        if tts_is_espeak:
            # eSpeak: Full speed and pitch control
            st.session_state.settings['speed'] = st.slider(
                "Speed (wpm)", 80, 450, st.session_state.settings['speed'], 10,
                help="Lower = slower speech (eSpeak only)"
            )
            
            st.session_state.settings['pitch'] = st.slider(
                "Pitch", 0, 99, st.session_state.settings['pitch'], 5,
                help="Voice pitch (eSpeak only)"
            )
        else:
            # Google TTS: Limited speed control (normal/slow only)
            st.session_state.settings['gtts_slow'] = st.checkbox(
                "Slow speech",
                value=st.session_state.settings.get('gtts_slow', False),
                help="Enable slower speech (~50% speed). Google TTS only supports normal or slow."
            )
            st.caption("💡 For more speed control, change the speed settings on the playback control (⋮)")
        
        # Get available voices for current language and TTS engine
        tts_engine = st.session_state.settings['tts_engine']
        available_voices = lang_config['voices'][tts_engine]
        
        # Make sure current voice is valid for selected language, otherwise use first available
        current_voice = st.session_state.settings.get('voice', available_voices[0])
        if current_voice not in available_voices:
            current_voice = available_voices[0]
            st.session_state.settings['voice'] = current_voice
        
        st.session_state.settings['voice'] = st.selectbox(
            "Voice",
            available_voices,
            index=available_voices.index(current_voice),
            help=f"Available voices for {st.session_state.language}"
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
        
        st.markdown("**🎚️ Audio Processing**")
        
        st.session_state.settings['silence_threshold'] = st.slider(
            "Silence Trim Threshold",
            min_value=0.001,
            max_value=0.1,
            value=st.session_state.settings.get('silence_threshold', 0.01),
            step=0.001,
            format="%.3f",
            help="Audio above this threshold (% of max) is kept as speech. Lower = keep more audio (may include noise). Higher = more aggressive trimming (may cut speech ends). Default: 0.01"
        )
        
        use_wav = st.checkbox(
            "Use WAV audio format",
            value=st.session_state.settings.get('use_wav_audio', False),
            help="Enable if TTS audio doesn't play on your device (iOS Safari compatibility). Converts MP3→WAV.",
            key="use_wav_checkbox"
        )
        # Update setting immediately when checkbox changes
        if use_wav != st.session_state.settings.get('use_wav_audio', False):
            st.session_state.settings['use_wav_audio'] = use_wav
            save_settings(st.session_state.settings)
            st.info("WAV audio setting saved")
        
        if st.button("💾 Save Settings"):
            save_settings(st.session_state.settings)
            st.success("Settings saved!")
        
        st.markdown("---")
        
        # Session info
        st.header("📊 Current Session")
        current_session = st.session_state.current_sessions[st.session_state.language]
        practice_count = len(current_session["practices"])
        st.metric("Practices", practice_count)
        
        if practice_count > 0:
            perfect = sum(1 for p in current_session["practices"] if p.get("exact_match", False))
            st.metric("Perfect", f"{perfect}/{practice_count}")
            
            if not st.session_state.session_saved:
                st.warning(f"⚠️ {practice_count} unsaved practice(s)")
                if st.button("💾 Save Session Now"):
                    save_current_session()
        
        # Documentation links
        st.markdown("---")
        st.header("📚 Help & Docs")
        st.markdown("""
        **📖 Guides:**
        - [User Guide](https://github.com/fairflow/espeak-ng-pt-br/blob/main/app-docs/USER_GUIDE.md) - How to use the app
        - [Testing Guide](https://github.com/fairflow/espeak-ng-pt-br/blob/main/app-docs/TESTING_GUIDE.md) - Report bugs & test
        - [All Documentation](https://github.com/fairflow/espeak-ng-pt-br/tree/main/app-docs)
        
        **💬 Support:**
        - Email: matthew@fairflow.co.uk
        - Discord: [Coming soon]
        """)
        
        # Version info
        st.markdown("---")
        st.caption(f"**{__app_name__}**")
        st.caption(f"Version {__version__}")
        
        # CCS Testing Framework Controls
        if CCS_AVAILABLE:
            st.markdown("---")
            st.header("🧪 CCS Testing")
            st.session_state.ccs_test.render_toggle_ui()
            if st.session_state.ccs_test.enabled:
                st.session_state.ccs_test.render_validation_ui()
    
    # Main content - Tabs
    tab1, tab2, tab3 = st.tabs([
        "🎯 Quick Practice",
        "📊 Statistics",
        "📜 History"
    ])
    
    # Tab 1: Quick Practice
    with tab1:
        st.header("Quick Practice")
        
        # Help info for new users
        current_session = st.session_state.current_sessions[st.session_state.language]
        if len(current_session["practices"]) == 0:
            st.info("👋 **New here?** Check the [User Guide](https://github.com/fairflow/espeak-ng-pt-br/blob/main/app-docs/USER_GUIDE.md) in the sidebar for step-by-step instructions!")
        
        # Phrase list import feature
        with st.expander("📁 Import Phrase List (Optional)"):
            st.write("Upload a text file with one phrase per line for structured practice.")
            uploaded_file = st.file_uploader(
                "Choose a text file",
                type=['txt'],
                help="Upload a .txt file with one phrase per line. Empty lines are ignored."
            )
            
            if uploaded_file is not None:
                try:
                    # Read and parse the file
                    content = uploaded_file.read().decode('utf-8')
                    raw_lines = [line.strip() for line in content.split('\n') if line.strip()]
                    
                    # Parse phrases - support both simple and enhanced format
                    # Enhanced format: "Portuguese | English translation | [IPA]"
                    # Simple format: "Portuguese"
                    phrases = []
                    for line in raw_lines:
                        if '|' in line:
                            # Enhanced format with translation
                            parts = [p.strip() for p in line.split('|')]
                            phrase_dict = {
                                'text': parts[0],
                                'translation': parts[1] if len(parts) > 1 else None,
                                'ipa': parts[2] if len(parts) > 2 else None
                            }
                            phrases.append(phrase_dict)
                        else:
                            # Simple format - just the text
                            phrases.append({'text': line, 'translation': None, 'ipa': None})
                    
                    st.success(f"✓ Loaded {len(phrases)} phrases")
                    
                    # Initialize phrase list in session state
                    if 'phrase_list' not in st.session_state or st.session_state.phrase_list != phrases:
                        st.session_state.phrase_list = phrases
                        st.session_state.current_phrase_index = 0
                        # Clear last result when loading new list
                        st.session_state.last_result = None
                    
                    # Show sample of phrases
                    if len(phrases) <= 5:
                        st.write("**Phrases:**")
                        for p in phrases:
                            st.write(f"• {p['text']}")
                    else:
                        sample_texts = [p['text'] for p in phrases[:3]]
                        st.write(f"**Sample phrases:** {', '.join(sample_texts)}, ...")
                        
                except Exception as e:
                    st.error(f"Error reading file: {e}")
            
            if 'phrase_list' in st.session_state and st.session_state.phrase_list:
                if st.button("🗑️ Clear Phrase List"):
                    st.session_state.phrase_list = []
                    st.session_state.current_phrase_index = 0
                    st.session_state.last_result = None
                    st.rerun()
        
        # Determine practice mode
        guided_mode = 'phrase_list' in st.session_state and st.session_state.phrase_list
        
        # MODE 1: Guided List Practice
        if guided_mode:
            st.markdown("---")
            st.subheader("📚 Guided Practice Mode")
            
            # Progress and navigation
            total_phrases = len(st.session_state.phrase_list)
            current_idx = st.session_state.current_phrase_index
            current_phrase_obj = st.session_state.phrase_list[current_idx]
            # Handle both dict and string formats for backward compatibility
            if isinstance(current_phrase_obj, dict):
                current_phrase = current_phrase_obj['text']
                phrase_translation = current_phrase_obj.get('translation')
                phrase_ipa = current_phrase_obj.get('ipa')
            else:
                current_phrase = current_phrase_obj
                phrase_translation = None
                phrase_ipa = None
            
            # Track phrase changes to show feedback
            if 'last_phrase_index' not in st.session_state:
                st.session_state.last_phrase_index = current_idx
            
            if st.session_state.last_phrase_index != current_idx:
                st.success(f"✓ Moved to phrase #{current_idx + 1}")
                st.session_state.last_phrase_index = current_idx
            
            # Progress bar
            progress = (current_idx + 1) / total_phrases
            st.progress(progress, text=f"Phrase {current_idx + 1} of {total_phrases}")
            
            # Navigation buttons
            # Check if we're in edit mode
            in_edit_mode = st.session_state.get('edit_mode', False)
            
            col1, col2, col3, col4 = st.columns([1, 1, 2, 1])
            with col1:
                # Disable navigation in edit mode to avoid confusion
                prev_disabled = (current_idx == 0) or in_edit_mode
                if st.button("⬅️ Previous", disabled=prev_disabled, key="nav_prev",
                           help="Navigation disabled in edit mode" if in_edit_mode else None):
                    st.session_state.current_phrase_index -= 1
                    # Keep result when navigating
                    st.rerun()
            with col2:
                # Disable navigation in edit mode to avoid confusion
                next_disabled = (current_idx >= total_phrases - 1) or in_edit_mode
                if st.button("Next ➡️", disabled=next_disabled, key="nav_next",
                           help="Navigation disabled in edit mode" if in_edit_mode else None):
                    st.session_state.current_phrase_index += 1
                    # Keep result when navigating
                    st.rerun()
            with col3:
                # DISABLED: Dropdown for jumping with phrase preview
                # This causes a critical async bug where the phrase shown during recording
                # is different from the phrase used for comparison when Check Pronunciation
                # is clicked. The selectbox triggers state updates at unpredictable times,
                # creating race conditions. May investigate Streamlit workarounds later.
                # 
                # jump_to = st.selectbox(
                #     "Jump to phrase:",
                #     options=range(total_phrases),
                #     index=current_idx,
                #     format_func=lambda i: f"{i+1}. {st.session_state.phrase_list[i][:40]}{'...' if len(st.session_state.phrase_list[i]) > 40 else ''}",
                #     key="phrase_jump_select"
                # )
                # if jump_to != current_idx:
                #     st.session_state.current_phrase_index = jump_to
                #     st.rerun()
                st.write("")  # Spacer for button alignment
            with col4:
                # Edit button - disabled when in edit mode
                if 'edit_mode' not in st.session_state:
                    st.session_state.edit_mode = False
                    
                # Disable Edit button when already in edit mode (grayed out)
                if st.button("✏️ Edit", key="toggle_edit", 
                            help="Edit current phrase or type your own",
                            disabled=st.session_state.edit_mode):
                    st.session_state.edit_mode = True
                    st.rerun()
            
            st.markdown("---")
            
            # Display current phrase - editable or fixed
            if st.session_state.edit_mode:
                st.markdown("### ✏️ Edit Mode:")
                st.caption("Edit the phrase below or type something completely different")
                text = st.text_input(
                    "Phrase to practice:",
                    value=current_phrase,
                    key="edit_phrase_input"
                )
                if st.button("📚 Return to Guided Mode", key="back_to_guided"):
                    st.session_state.edit_mode = False
                    st.rerun()
            else:
                st.markdown("### 🎯 Current Phrase:")
                # Display phrase in large, bold text
                st.markdown(f"# **{current_phrase}**")
                
                # Show translation/IPA if available
                if phrase_translation or phrase_ipa:
                    with st.expander("📖 Translation & Reference", expanded=False):
                        if phrase_translation:
                            st.markdown(f"**🇬🇧 English:** {phrase_translation}")
                        if phrase_ipa:
                            st.markdown(f"**📚 Reference IPA:** {phrase_ipa}")
                            st.caption("Compare with eSpeak IPA generated below")
                
                st.caption("This phrase is automatically selected from your list. Click 'Edit' above to modify it.")
                # Use this phrase for practice
                text = current_phrase
            
        # MODE 2: Free Text Practice
        else:
            st.write("Practice any word or phrase you like")
            
            # Show navigation buttons (disabled) for consistency
            col1, col2, col3 = st.columns([1, 1, 4])
            with col1:
                st.button("⬅️ Previous", disabled=True, key="nav_prev_disabled", 
                         help="Navigation only available in guided mode")
            with col2:
                st.button("Next ➡️", disabled=True, key="nav_next_disabled",
                         help="Navigation only available in guided mode")
            with col3:
                st.write("")  # Spacing
            
            st.markdown("---")
            text = st.text_input("Enter word or phrase:", key="practice_text_free")
        
        if text:
            # Show target audio directly - one click to play
            st.write("🎯 **Target pronunciation:**")
            with st.spinner("Generating audio..."):
                audio_bytes, audio_format = generate_target_audio(text, st.session_state.settings)
                st.audio(audio_bytes, format=audio_format, autoplay=False)
            
            st.markdown("---")
            st.write("🎙️ **Now record your pronunciation:**")
            st.info("💡 Wait for the recording icon to turn red before speaking. The app will automatically trim silence and enforce Portuguese language detection.")
            
            # Streamlit's built-in audio input with dynamic key
            audio_data = st.audio_input("Click to record", key=f"audio_input_{st.session_state.audio_input_key}")
            
            if audio_data:
                st.write("▶️ **Your recording:**")
                st.audio(audio_data, format='audio/wav')
                
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
                        # Clear the recording, results, and force widget reset
                        st.session_state.last_result = None
                        st.session_state.audio_input_key += 1  # Change key to reset widget
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
                
                # Show target audio directly
                tts_label = "Google TTS" if st.session_state.settings.get('tts_engine', 'gtts') == 'gtts' else "eSpeak"
                st.write(f"🔊 **{tts_label}:**")
                audio_bytes, audio_format = generate_target_audio(result['target'], st.session_state.settings)
                st.audio(audio_bytes, format=audio_format)
            
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
                    
                    st.write("**Normalised phonemes (spaces removed for comparison):**")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        # Use IPA (not eIPA) for user-friendly display
                        correct_ipa_normalized = result.get('correct_ipa', '').replace(" ", "")
                        st.code(correct_ipa_normalized, language=None)
                        st.caption(f"Target ({len(correct_ipa_normalized)} chars)")
                    with col_b:
                        user_ipa_normalized = result.get('user_ipa', '').replace(" ", "")
                        st.code(user_ipa_normalized, language=None)
                        st.caption(f"Your Pronunciation ({len(user_ipa_normalized)} chars)")
                    
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
                
                # Show trimmed recording (what was actually recognized)
                if result.get('user_audio_trimmed_bytes'):
                    st.write("🔊 **Your (trimmed) recording:**")
                    st.audio(result['user_audio_trimmed_bytes'], format='audio/wav')
                    st.caption("This is the audio that was actually sent to the recognition engine (after silence trimming with 200ms padding).")
                
                # Show TTS of what was recognized (if different)
                if result['recognized'] != result['target']:
                    tts_label = "Google TTS" if st.session_state.settings.get('tts_engine', 'gtts') == 'gtts' else "eSpeak"
                    st.write(f"🔊 **Recognized text ({tts_label}):**")
                    audio_bytes, audio_format = generate_target_audio(result['recognized'], st.session_state.settings)
                    st.audio(audio_bytes, format=audio_format)
            
            # Optional: Hear eSpeak phoneme pronunciation (local development only)
            if IS_LOCAL_DEV and not result["exact_match"]:
                st.markdown("---")
                st.subheader("Compare Phoneme Sounds (eSpeak)")
                st.caption("🔧 Development feature - requires local audio device")
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
        current_session = st.session_state.current_sessions[st.session_state.language]
        if current_session["practices"]:
            st.subheader("🔵 Current Session")
            practices = current_session["practices"]
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
    
    # CCS Testing: Extract app state after UI renders (if testing enabled)
    if CCS_AVAILABLE and st.session_state.ccs_test.enabled:
        st.session_state.ccs_test.extract_app_state_from_streamlit()


if __name__ == "__main__":
    main()
