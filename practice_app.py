#!/usr/bin/env python3
"""
practice_app.py - Interactive Brazilian Portuguese Pronunciation Practice App

Features:
- Save/load user preferences (speed, pitch, voice, etc.)
- Track practice sessions and progress
- Multiple practice modes
- Audio file management
- Session replay and review
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

try:
    from pronunciation_trainer import PronunciationTrainer
except ImportError:
    print("Error: Run from espeak-ng directory with venv activated")
    sys.exit(1)


class PracticeApp:
    """Interactive pronunciation practice application"""
    
    def __init__(self, config_file: str = "practice_config.json"):
        self.config_file = Path(config_file)
        self.history_file = Path("practice_history.json")
        self.audio_dir = Path("practice_audio")
        self.audio_dir.mkdir(exist_ok=True)
        
        # Default settings
        self.settings = {
            "speed": 140,
            "pitch": 35,
            "voice": "pt-br",
            "model": "base",
            "duration": 3,
        }
        
        # Load saved settings
        self.load_settings()
        
        # Session history
        self.history: List[Dict] = []
        self.load_history()
        
        # Current session
        self.current_session = {
            "date": datetime.now().isoformat(),
            "practices": []
        }
    
    def load_settings(self):
        """Load user settings from config file"""
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    saved = json.load(f)
                    self.settings.update(saved)
                print(f"✓ Loaded settings from {self.config_file}")
            except Exception as e:
                print(f"⚠ Could not load settings: {e}")
    
    def save_settings(self):
        """Save current settings to config file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            print(f"✓ Settings saved to {self.config_file}")
        except Exception as e:
            print(f"⚠ Could not save settings: {e}")
    
    def load_history(self):
        """Load practice history"""
        if self.history_file.exists():
            try:
                with open(self.history_file) as f:
                    self.history = json.load(f)
            except Exception as e:
                print(f"⚠ Could not load history: {e}")
    
    def save_history(self):
        """Save practice history"""
        try:
            # Add current session if it has practices
            if self.current_session["practices"]:
                self.history.append(self.current_session)
            
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
            print(f"✓ History saved to {self.history_file}")
        except Exception as e:
            print(f"⚠ Could not save history: {e}")
    
    def show_settings(self):
        """Display current settings"""
        print("\n" + "=" * 60)
        print("⚙️  CURRENT SETTINGS")
        print("=" * 60)
        print(f"Speed:    {self.settings['speed']} wpm (80-450, lower=slower)")
        print(f"Pitch:    {self.settings['pitch']} (0-99)")
        print(f"Voice:    {self.settings['voice']}")
        print(f"Model:    {self.settings['model']}")
        print(f"Duration: {self.settings['duration']} seconds")
        print("=" * 60)
    
    def edit_settings(self):
        """Interactive settings editor"""
        print("\n📝 Edit Settings")
        print("(Press Enter to keep current value)")
        
        try:
            # Speed
            speed = input(f"Speed [{self.settings['speed']}]: ").strip()
            if speed:
                self.settings['speed'] = int(speed)
            
            # Pitch
            pitch = input(f"Pitch [{self.settings['pitch']}]: ").strip()
            if pitch:
                self.settings['pitch'] = int(pitch)
            
            # Voice
            print(f"\nVoice options: pt-br (Brazilian), pt (European)")
            voice = input(f"Voice [{self.settings['voice']}]: ").strip()
            if voice:
                self.settings['voice'] = voice
            
            # Model
            print(f"\nModel options: tiny, base, small, medium, large")
            model = input(f"Model [{self.settings['model']}]: ").strip()
            if model:
                self.settings['model'] = model
            
            # Duration
            duration = input(f"Recording duration [{self.settings['duration']}]: ").strip()
            if duration:
                self.settings['duration'] = int(duration)
            
            self.save_settings()
            print("\n✓ Settings updated!")
            
        except ValueError as e:
            print(f"\n⚠ Invalid input: {e}")
        except KeyboardInterrupt:
            print("\n⚠ Settings edit cancelled")
    
    def quick_practice(self):
        """Quick practice mode - single word/phrase"""
        print("\n🎯 Quick Practice")
        text = input("Enter word or phrase to practice: ").strip()
        
        if not text:
            print("⚠ No text entered")
            return
        
        # Initialize trainer
        trainer = PronunciationTrainer(
            whisper_model=self.settings['model'],
            voice=self.settings['voice']
        )
        
        # Practice
        result = trainer.practice_word(
            text,
            duration=self.settings['duration'],
            speed=self.settings['speed'],
            pitch=self.settings['pitch']
        )
        
        # Save to session
        self.current_session["practices"].append({
            "time": datetime.now().isoformat(),
            "target": result["target"],
            "recognized": result["recognized"],
            "correct_phonemes": result["correct_phonemes"],
            "user_phonemes": result["user_phonemes"],
            "match": result["exact_match"],
            "similarity": result["similarity"]
        })
        
        # Show result
        if result["exact_match"]:
            print("\n🎉 PERFECT MATCH! Well done!")
        else:
            print(f"\n📊 Score: {result['similarity']:.1%}")
    
    def sentence_practice(self):
        """Sentence practice with auto-duration"""
        print("\n📝 Sentence Practice")
        sentence = input("Enter sentence: ").strip()
        
        if not sentence:
            print("⚠ No sentence entered")
            return
        
        # Auto-calculate duration
        words = len(sentence.split())
        duration = max(5, int(words / 2.5) + 2)
        
        print(f"\n📏 {words} words → {duration} seconds recording time")
        
        # Initialize trainer
        trainer = PronunciationTrainer(
            whisper_model=self.settings['model'],
            voice=self.settings['voice']
        )
        
        # Practice
        result = trainer.practice_word(
            sentence,
            duration=duration,
            speed=self.settings['speed'],
            pitch=self.settings['pitch']
        )
        
        # Save to session
        self.current_session["practices"].append({
            "time": datetime.now().isoformat(),
            "target": result["target"],
            "recognized": result["recognized"],
            "match": result["exact_match"],
            "similarity": result["similarity"]
        })
    
    def practice_from_file(self):
        """Import text from file for practice"""
        print("\n📂 Practice from File")
        filename = input("Enter filename: ").strip()
        
        if not filename:
            print("⚠ No filename entered")
            return
        
        try:
            lines = Path(filename).read_text().strip().split('\n')
            lines = [l.strip() for l in lines if l.strip()]
            
            print(f"\n📚 Found {len(lines)} items")
            print("Practice all? (y/n): ", end="")
            
            if input().lower() != 'y':
                return
            
            trainer = PronunciationTrainer(
                whisper_model=self.settings['model'],
                voice=self.settings['voice']
            )
            
            for i, text in enumerate(lines, 1):
                print(f"\n{'=' * 60}")
                print(f"Item {i}/{len(lines)}")
                print(f"{'=' * 60}\n")
                
                result = trainer.practice_word(
                    text,
                    duration=self.settings['duration'],
                    speed=self.settings['speed'],
                    pitch=self.settings['pitch']
                )
                
                self.current_session["practices"].append({
                    "time": datetime.now().isoformat(),
                    "target": result["target"],
                    "recognized": result["recognized"],
                    "match": result["exact_match"],
                    "similarity": result["similarity"]
                })
                
                if i < len(lines):
                    input("\nPress Enter for next item...")
            
        except FileNotFoundError:
            print(f"⚠ File not found: {filename}")
        except Exception as e:
            print(f"⚠ Error: {e}")
    
    def show_statistics(self):
        """Display practice statistics"""
        print("\n" + "=" * 60)
        print("📊 PRACTICE STATISTICS")
        print("=" * 60)
        
        if not self.history and not self.current_session["practices"]:
            print("No practice history yet!")
            return
        
        # Current session stats
        if self.current_session["practices"]:
            print("\n🔵 Current Session:")
            practices = self.current_session["practices"]
            perfect = sum(1 for p in practices if p["match"])
            avg_sim = sum(p["similarity"] for p in practices) / len(practices)
            
            print(f"  Practices: {len(practices)}")
            print(f"  Perfect: {perfect} ({perfect/len(practices):.1%})")
            print(f"  Avg Similarity: {avg_sim:.1%}")
        
        # Overall stats
        if self.history:
            print("\n📈 All Time:")
            total_practices = sum(len(s["practices"]) for s in self.history)
            total_perfect = sum(
                sum(1 for p in s["practices"] if p["match"])
                for s in self.history
            )
            
            all_similarities = [
                p["similarity"]
                for s in self.history
                for p in s["practices"]
            ]
            
            if all_similarities:
                avg_all = sum(all_similarities) / len(all_similarities)
                print(f"  Total Practices: {total_practices}")
                print(f"  Total Perfect: {total_perfect} ({total_perfect/total_practices:.1%})")
                print(f"  Overall Avg: {avg_all:.1%}")
            
            print(f"\n  Sessions: {len(self.history)}")
            print(f"  Last session: {self.history[-1]['date'][:10]}")
        
        print("=" * 60)
    
    def review_session(self):
        """Review practice session history"""
        print("\n" + "=" * 60)
        print("📜 SESSION HISTORY")
        print("=" * 60)
        
        if not self.history:
            print("No previous sessions")
            return
        
        # Show recent sessions
        print("\nRecent sessions:")
        for i, session in enumerate(reversed(self.history[-10:]), 1):
            date = session["date"][:10]
            count = len(session["practices"])
            perfect = sum(1 for p in session["practices"] if p["match"])
            print(f"  {i}. {date} - {count} practices ({perfect} perfect)")
        
        # Option to view details
        print("\nEnter session number to view details (or Enter to go back): ", end="")
        choice = input().strip()
        
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(self.history[-10:]):
                session = list(reversed(self.history[-10:]))[idx]
                self.show_session_details(session)
    
    def show_session_details(self, session: Dict):
        """Show detailed session information"""
        print("\n" + "=" * 60)
        print(f"Session: {session['date']}")
        print("=" * 60)
        
        for i, practice in enumerate(session["practices"], 1):
            status = "✅" if practice["match"] else f"📊 {practice['similarity']:.1%}"
            print(f"\n{i}. {status}")
            print(f"   Target:     {practice['target']}")
            print(f"   Recognized: {practice['recognized']}")
            if not practice["match"]:
                # Handle old session data that might not have phoneme fields
                if "correct_phonemes" in practice:
                    print(f"   Correct:    {practice['correct_phonemes']}")
                if "user_phonemes" in practice:
                    print(f"   Yours:      {practice['user_phonemes']}")
    
    def main_menu(self):
        """Display main menu and handle user choice"""
        while True:
            print("\n" + "=" * 60)
            print("🇧🇷 BRAZILIAN PORTUGUESE PRONUNCIATION PRACTICE")
            print("=" * 60)
            print("\n1. Quick Practice (word/phrase)")
            print("2. Sentence Practice (auto-duration)")
            print("3. Practice from File")
            print("4. View Statistics")
            print("5. Review Session History")
            print("6. Settings")
            print("7. View Current Settings")
            print("8. Save & Exit")
            print("9. Exit without Saving")
            
            choice = input("\nChoose option (1-9): ").strip()
            
            if choice == '1':
                self.quick_practice()
            elif choice == '2':
                self.sentence_practice()
            elif choice == '3':
                self.practice_from_file()
            elif choice == '4':
                self.show_statistics()
            elif choice == '5':
                self.review_session()
            elif choice == '6':
                self.edit_settings()
            elif choice == '7':
                self.show_settings()
            elif choice == '8':
                self.save_history()
                self.save_settings()
                print("\n👋 Session saved. Até logo!")
                break
            elif choice == '9':
                print("\n👋 Exiting without saving. Até logo!")
                break
            else:
                print("\n⚠ Invalid choice. Please enter 1-9.")


def main():
    """Main entry point"""
    print("\n🎓 Welcome to Portuguese Pronunciation Practice!")
    print("Make sure you've activated the virtual environment:")
    print("  source venv/bin/activate\n")
    
    try:
        app = PracticeApp()
        app.main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Practice interrupted. Até logo!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
