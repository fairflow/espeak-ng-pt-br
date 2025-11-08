#!/usr/bin/env python3
"""
streamlit_app.py - Streamlit Web Interface for Brazilian Portuguese Pronunciation Practice

Run with: streamlit run streamlit_app.py
"""

import streamlit as st
import json
import warnings
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import tempfile
import os

# Suppress FP16 warning from Whisper on CPU
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")

from pronunciation_trainer import PronunciationTrainer


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


def practice_word_streamlit(text: str, audio_bytes: bytes, speed: int, pitch: int, voice: str, model: str):
    """
    Practice a word/phrase using pre-recorded audio from Streamlit
    
    Args:
        text: Target word/phrase
        audio_bytes: Audio data from Streamlit audio recorder
        speed: Speech speed
        pitch: Speech pitch
        voice: eSpeak voice
        model: Whisper model
        
    Returns:
        Practice result dictionary
    """
    try:
        # Save audio bytes to temporary file
        temp_audio = "temp_streamlit_recording.wav"
        with open(temp_audio, 'wb') as f:
            f.write(audio_bytes)
        
        # Initialize trainer without loading Whisper yet (to avoid reload)
        if 'trainer' not in st.session_state or st.session_state.get('trainer_model') != model:
            st.session_state.trainer = PronunciationTrainer(whisper_model=model, voice=voice)
            st.session_state.trainer_model = model
        
        trainer = st.session_state.trainer
        
        # Get correct pronunciation
        correct_phonemes = trainer.get_phonemes(text)
        correct_ipa = trainer.get_ipa(text)
        
        # Speak the correct pronunciation
        trainer.speak_text(text, speed=speed, pitch=pitch)
        
        # Transcribe user's audio
        recognized_text, whisper_result = trainer.transcribe_audio(
            temp_audio,
            prompt=text,
            temperature=0.0
        )
        
        # Check recognition quality
        is_valid, warning = trainer.check_recognition_quality(recognized_text, text)
        quality_issues = [warning] if not is_valid and warning else []
        
        # Get phonemes of what they said
        user_phonemes = trainer.get_phonemes(recognized_text)
        user_ipa = trainer.get_ipa(recognized_text)
        
        # Compare
        exact_match, similarity = trainer.compare_phonemes(user_phonemes, correct_phonemes)
        
        # Clean up temp file
        Path(temp_audio).unlink(missing_ok=True)
        
        result = {
            "target": text,
            "recognized": recognized_text,
            "correct_phonemes": correct_phonemes,
            "user_phonemes": user_phonemes,
            "correct_ipa": correct_ipa,
            "user_ipa": user_ipa,
            "exact_match": exact_match,
            "similarity": similarity,
            "quality_issues": quality_issues
        }
        
        # Save to current session
        st.session_state.current_session["practices"].append({
            "time": datetime.now().isoformat(),
            "target": result["target"],
            "recognized": result["recognized"],
            "correct_phonemes": result["correct_phonemes"],
            "user_phonemes": result["user_phonemes"],
            "correct_ipa": result.get("correct_ipa", ""),
            "user_ipa": result.get("user_ipa", ""),
            "match": result["exact_match"],
            "similarity": result["similarity"]
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
        
        st.session_state.settings['duration'] = st.number_input(
            "Recording Duration (seconds)",
            min_value=1, max_value=10,
            value=st.session_state.settings['duration']
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
            perfect = sum(1 for p in st.session_state.current_session["practices"] if p["match"])
            st.metric("Perfect", f"{perfect}/{practice_count}")
            
            if not st.session_state.session_saved:
                st.warning(f"⚠️ {practice_count} unsaved practice(s)")
                if st.button("💾 Save Session Now"):
                    save_current_session()
    
    # Main content - Tabs for different modes
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Quick Practice",
        "📝 Sentence Practice", 
        "📂 File Practice",
        "📊 Statistics",
        "📜 History"
    ])
    
    # Tab 1: Quick Practice
    with tab1:
        st.header("Quick Practice")
        st.write("Practice a single word or short phrase")
        
        text = st.text_input("Enter word or phrase:", key="quick_text")
        
        if text:
            st.write("👇 Record your pronunciation using the audio input below:")
            
            # Streamlit's built-in audio input
            audio_bytes = st.audio_input("Record your pronunciation", key="quick_audio")
            
            if audio_bytes:
                st.audio(audio_bytes, format="audio/wav")
                
                if st.button("✅ Submit Recording", key="quick_submit", type="primary"):
                    with st.spinner("Processing your pronunciation..."):
                        result = practice_word_streamlit(
                            text,
                            audio_bytes.getvalue(),
                            st.session_state.settings['speed'],
                            st.session_state.settings['pitch'],
                            st.session_state.settings['voice'],
                            st.session_state.settings['model']
                        )
        else:
            st.info("👆 Enter a word or phrase above to begin")
        
        # Show last result
        if st.session_state.last_result:
            st.markdown("---")
            result = st.session_state.last_result
            
            if result["exact_match"]:
                st.success("🎉 PERFECT MATCH! Well done!")
            else:
                st.info(f"📊 Score: {result['similarity']:.1%}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Target:**", result["target"])
                st.write("**Correct eIPA:**", result["correct_phonemes"])
                if result.get("correct_ipa"):
                    st.write("**Correct IPA:**", result["correct_ipa"])
            
            with col2:
                st.write("**Your speech:**", result["recognized"])
                st.write("**Your eIPA:**", result["user_phonemes"])
                if result.get("user_ipa"):
                    st.write("**Your IPA:**", result["user_ipa"])
            
            # Quality warnings
            if result.get("quality_issues"):
                st.warning("⚠️ Recognition quality issues detected:")
                for issue in result["quality_issues"]:
                    st.write(f"- {issue}")
    
    # Tab 2: Sentence Practice
    with tab2:
        st.header("Sentence Practice")
        st.write("Practice longer sentences")
        
        sentence = st.text_area("Enter sentence:", key="sentence_text", height=100)
        
        if sentence:
            words = len(sentence.split())
            st.info(f"📏 {words} words - Record as much time as you need")
            
            st.write("� Click the microphone button below to record your pronunciation:")
            
            # Audio recorder for sentences
            audio_bytes = audio_recorder(
                text="🎤 Record Audio",
                recording_color="#e74c3c",
                neutral_color="#3498db",
                icon_name="microphone",
                icon_size="2x",
                key="sentence_recorder"
            )
            
            if audio_bytes:
                st.audio(audio_bytes, format="audio/wav")
                
                if st.button("✅ Submit Recording", key="sentence_submit", type="primary"):
                    with st.spinner("Processing your pronunciation..."):
                        result = practice_word_streamlit(
                            sentence,
                            audio_bytes,
                            st.session_state.settings['speed'],
                            st.session_state.settings['pitch'],
                            st.session_state.settings['voice'],
                            st.session_state.settings['model']
                        )
        else:
            st.info("👆 Enter a sentence above to begin")
    
    # Tab 3: File Practice
    with tab3:
        st.header("Practice from File")
        st.write("Upload a text file with words/phrases to practice (one per line)")
        
        uploaded_file = st.file_uploader("Choose a file", type=['txt'])
        
        if uploaded_file:
            content = uploaded_file.read().decode('utf-8')
            lines = [l.strip() for l in content.split('\n') if l.strip() and not l.strip().startswith('#')]
            
            st.success(f"📚 Found {len(lines)} items")
            
            # Show preview
            with st.expander("Preview items"):
                for i, line in enumerate(lines[:10], 1):
                    st.write(f"{i}. {line}")
                if len(lines) > 10:
                    st.write(f"... and {len(lines) - 10} more")
            
            st.warning("⚠️ File practice mode: You'll need to record each item individually")
            
            # Initialize file practice state
            if 'file_practice_index' not in st.session_state:
                st.session_state.file_practice_index = 0
                st.session_state.file_practice_lines = []
            
            # Start button
            if st.session_state.file_practice_index == 0:
                if st.button("▶️ Start Practice", key="file_start", type="primary"):
                    st.session_state.file_practice_lines = lines
                    st.session_state.file_practice_index = 1
                    st.rerun()
            
            # Practice current item
            if st.session_state.file_practice_index > 0 and st.session_state.file_practice_index <= len(st.session_state.file_practice_lines):
                current_index = st.session_state.file_practice_index
                current_text = st.session_state.file_practice_lines[current_index - 1]
                
                st.progress(current_index / len(st.session_state.file_practice_lines))
                st.subheader(f"Item {current_index}/{len(st.session_state.file_practice_lines)}: {current_text}")
                
                # Audio recorder
                audio_bytes = audio_recorder(
                    text="🎤 Record Audio",
                    recording_color="#e74c3c",
                    neutral_color="#3498db",
                    icon_name="microphone",
                    icon_size="2x",
                    key=f"file_recorder_{current_index}"
                )
                
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/wav")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ Submit & Next", key=f"file_submit_{current_index}", type="primary"):
                            with st.spinner("Processing..."):
                                result = practice_word_streamlit(
                                    current_text,
                                    audio_bytes,
                                    st.session_state.settings['speed'],
                                    st.session_state.settings['pitch'],
                                    st.session_state.settings['voice'],
                                    st.session_state.settings['model']
                                )
                            
                            # Move to next item
                            if current_index < len(st.session_state.file_practice_lines):
                                st.session_state.file_practice_index += 1
                                st.rerun()
                            else:
                                st.session_state.file_practice_index = 0
                                st.success("✓ All items completed!")
                                st.balloons()
                    
                    with col2:
                        if st.button("⏭️ Skip", key=f"file_skip_{current_index}"):
                            if current_index < len(st.session_state.file_practice_lines):
                                st.session_state.file_practice_index += 1
                                st.rerun()
                            else:
                                st.session_state.file_practice_index = 0
                                st.info("Practice session completed")
            
            elif st.session_state.file_practice_index > 0:
                # Completed
                st.success("🎉 All items completed!")
                if st.button("🔄 Restart Practice", key="file_restart"):
                    st.session_state.file_practice_index = 0
                    st.rerun()
    
    # Tab 4: Statistics
    with tab4:
        st.header("📊 Practice Statistics")
        
        # Current session stats
        if st.session_state.current_session["practices"]:
            st.subheader("🔵 Current Session")
            practices = st.session_state.current_session["practices"]
            perfect = sum(1 for p in practices if p["match"])
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
                sum(1 for p in s["practices"] if p["match"])
                for s in st.session_state.history
            )
            
            all_similarities = [
                p["similarity"]
                for s in st.session_state.history
                for p in s["practices"]
            ]
            
            if all_similarities:
                avg_all = sum(all_similarities) / len(all_similarities)
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Practices", total_practices)
                col2.metric("Total Perfect", f"{total_perfect} ({total_perfect/total_practices:.1%})")
                col3.metric("Overall Avg", f"{avg_all:.1%}")
                col4.metric("Sessions", len(st.session_state.history))
                
                last_date = st.session_state.history[-1]['date'][:10]
                st.info(f"Last session: {last_date}")
        else:
            st.info("No practice history yet. Start practicing to see statistics!")
    
    # Tab 5: History
    with tab5:
        st.header("📜 Session History")
        
        if not st.session_state.history:
            st.info("No previous sessions")
        else:
            # Show recent sessions
            st.subheader("Recent Sessions")
            
            for i, session in enumerate(reversed(st.session_state.history[-10:]), 1):
                date = session["date"][:10]
                count = len(session["practices"])
                perfect = sum(1 for p in session["practices"] if p["match"])
                
                with st.expander(f"{date} - {count} practices ({perfect} perfect)"):
                    for j, practice in enumerate(session["practices"], 1):
                        status = "✅" if practice["match"] else f"📊 {practice['similarity']:.1%}"
                        
                        st.markdown(f"**{j}. {status}**")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("Target:", practice['target'])
                            if "correct_phonemes" in practice:
                                st.write("Correct eIPA:", practice['correct_phonemes'])
                            if "correct_ipa" in practice and practice["correct_ipa"]:
                                st.write("Correct IPA:", practice['correct_ipa'])
                        
                        with col2:
                            st.write("Recognized:", practice['recognized'])
                            if "user_phonemes" in practice:
                                st.write("Your eIPA:", practice['user_phonemes'])
                            if "user_ipa" in practice and practice["user_ipa"]:
                                st.write("Your IPA:", practice['user_ipa'])
                        
                        st.markdown("---")


if __name__ == "__main__":
    main()
