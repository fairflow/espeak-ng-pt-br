"""
CCS-Based Testing Framework for Streamlit Portuguese Pronunciation App

This module implements a Calculus of Communicating Systems (CCS) inspired
testing framework where the app and user are modeled as dual agents with
complementary communication ports.

Key Concepts:
- App Agent: Offers capabilities (input ports) - what the app can do
- User Agent: Expresses desires (output ports) - what the user wants to do
- Port Matching: Successful interaction when complementary ports align
- State Tracking: Internal model of both app state and user intent
- Testing Oracle: User validates alignment between model and actual UI

Author: Testing framework for pronunciation training app
Date: November 2025
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple
from enum import Enum, auto
import json
import time


class PracticeMode(Enum):
    """High-level practice modes"""
    FREE_TEXT = auto()      # User types any phrase
    GUIDED_LIST = auto()    # User navigates through loaded phrase list
    GUIDED_EDIT = auto()    # User edits current phrase from list


class UIElement(Enum):
    """Visible UI elements that can be present or absent"""
    # Input elements
    TEXT_INPUT_FREE = auto()        # Free text input field
    TEXT_INPUT_EDIT = auto()        # Edit mode text input field
    AUDIO_RECORDER = auto()         # Recording widget
    
    # Display elements
    PHRASE_DISPLAY_BOLD = auto()    # Current phrase in bold/large text
    RESULTS_PANEL = auto()          # Pronunciation analysis results
    
    # Audio players - specific types tracked separately
    AUDIO_PLAYER_TARGET_PRACTICE = auto()     # Target TTS when entering practice
    AUDIO_PLAYER_USER_LIVE = auto()           # User's just-recorded audio
    AUDIO_PLAYER_TARGET_RESULTS = auto()      # Target TTS in results panel
    AUDIO_PLAYER_USER_RESULTS = auto()        # User's recording in results panel
    AUDIO_PLAYER_RECOGNIZED_TTS = auto()      # TTS of recognized text
    AUDIO_PLAYER_PHONEME_CORRECT = auto()     # eSpeak correct phonemes (on demand)
    AUDIO_PLAYER_PHONEME_USER = auto()        # eSpeak user phonemes (on demand)
    
    # Navigation elements
    PHRASE_LIST_UPLOADER = auto()   # File upload widget
    PREV_BUTTON = auto()            # Previous phrase button
    NEXT_BUTTON = auto()            # Next phrase button
    JUMP_SELECTOR = auto()          # Jump to phrase dropdown
    PROGRESS_BAR = auto()           # Progress indicator
    
    # Control buttons
    CHECK_BUTTON = auto()           # Check pronunciation button
    CLEAR_BUTTON = auto()           # Clear recording button
    EDIT_BUTTON = auto()            # Toggle edit mode button
    BACK_TO_LIST_BUTTON = auto()   # Return to list mode button
    CLEAR_LIST_BUTTON = auto()     # Clear phrase list button


class AppCapability(Enum):
    """What the app can accept/process (input ports)"""
    ACCEPT_TEXT_INPUT = auto()
    ACCEPT_AUDIO_RECORDING = auto()
    ACCEPT_FILE_UPLOAD = auto()
    ACCEPT_NAVIGATION_PREV = auto()
    ACCEPT_NAVIGATION_NEXT = auto()
    ACCEPT_JUMP_TO_PHRASE = auto()
    ACCEPT_MODE_TOGGLE = auto()
    ACCEPT_CLEAR_RECORDING = auto()
    ACCEPT_CLEAR_LIST = auto()
    
    # Audio provision capabilities - specific types
    PROVIDE_TARGET_AUDIO_PRACTICE = auto()    # Can play target during practice
    PROVIDE_USER_AUDIO_LIVE = auto()          # Can play back just-recorded audio
    PROVIDE_TARGET_AUDIO_RESULTS = auto()     # Can play target in results
    PROVIDE_USER_AUDIO_RESULTS = auto()       # Can play user recording in results
    PROVIDE_RECOGNIZED_AUDIO = auto()         # Can play TTS of recognized text
    PROVIDE_PHONEME_AUDIO_CORRECT = auto()    # Can play correct phonemes
    PROVIDE_PHONEME_AUDIO_USER = auto()       # Can play user phonemes
    PROVIDE_ANALYSIS_RESULTS = auto()


class UserIntent(Enum):
    """What the user wants to do (output ports)"""
    WANT_ENTER_TEXT = auto()
    WANT_RECORD_AUDIO = auto()
    WANT_UPLOAD_FILE = auto()
    WANT_GO_PREVIOUS = auto()
    WANT_GO_NEXT = auto()
    WANT_JUMP_TO_PHRASE = auto()
    WANT_TOGGLE_MODE = auto()
    WANT_CLEAR_RECORDING = auto()
    WANT_CLEAR_LIST = auto()
    WANT_SEE_RESULTS = auto()
    
    # Audio playback intents - specific types
    WANT_HEAR_TARGET_PRACTICE = auto()     # Want to hear target before recording
    WANT_HEAR_USER_LIVE = auto()           # Want to hear just-recorded audio
    WANT_HEAR_TARGET_RESULTS = auto()      # Want to hear target in results
    WANT_HEAR_USER_RESULTS = auto()        # Want to hear recording in results
    WANT_HEAR_RECOGNIZED = auto()          # Want to hear what ASR recognized
    WANT_HEAR_PHONEME_CORRECT = auto()     # Want to hear correct phoneme pronunciation
    WANT_HEAR_PHONEME_USER = auto()        # Want to hear user phoneme pronunciation


@dataclass
class AppState:
    """
    State of the app agent (what the app offers).
    This represents what capabilities and UI elements the app provides.
    """
    mode: PracticeMode = PracticeMode.FREE_TEXT
    current_text: str = ""                    # Current phrase being practiced
    phrase_list: List[str] = field(default_factory=list)
    current_phrase_index: int = 0
    has_recording: bool = False               # User has recorded audio
    has_results: bool = False                 # Pronunciation results available
    
    # Priority 2 improvements: Enhanced state tracking
    displayed_phrase_text: Optional[str] = None  # Actual phrase shown on screen
    current_score: Optional[float] = None        # Most recent similarity score
    recognized_text: Optional[str] = None        # ASR transcription of user's audio
    settings: Optional[Dict] = None              # App settings for reproducibility
    
    visible_elements: Set[UIElement] = field(default_factory=set)
    active_capabilities: Set[AppCapability] = field(default_factory=set)
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary for logging/debugging"""
        return {
            'mode': self.mode.name,
            'current_text': self.current_text,
            'phrase_list_size': len(self.phrase_list),
            'current_phrase_index': self.current_phrase_index,
            'has_recording': self.has_recording,
            'has_results': self.has_results,
            'displayed_phrase_text': self.displayed_phrase_text,
            'current_score': self.current_score,
            'recognized_text': self.recognized_text,
            'settings': self.settings,
            'visible_elements': [e.name for e in self.visible_elements],
            'active_capabilities': [c.name for c in self.active_capabilities]
        }
    
    def check_invariants(self) -> List[str]:
        """
        Check state invariants and return list of violations.
        This enables automated bug detection.
        """
        violations = []
        
        # Invariant: If has_results, must have has_recording
        if self.has_results and not self.has_recording:
            violations.append("Results exist but no recording (impossible state)")
        
        # Invariant: GUIDED_LIST requires phrase_list_size > 0
        if self.mode == PracticeMode.GUIDED_LIST and len(self.phrase_list) == 0:
            violations.append("GUIDED_LIST mode but empty phrase list")
        
        # Invariant: current_phrase_index must be in bounds
        if len(self.phrase_list) > 0:
            if self.current_phrase_index < 0:
                violations.append(f"Negative phrase index: {self.current_phrase_index}")
            elif self.current_phrase_index >= len(self.phrase_list):
                violations.append(f"Phrase index {self.current_phrase_index} out of bounds (size={len(self.phrase_list)})")
        
        # Invariant: If has_results, should have current_score
        if self.has_results and self.current_score is None:
            violations.append("Results exist but no score available")
        
        # Invariant: displayed_phrase_text should match expectations
        if self.mode == PracticeMode.GUIDED_LIST and len(self.phrase_list) > 0:
            expected_phrase = self.phrase_list[self.current_phrase_index]
            if self.displayed_phrase_text and self.displayed_phrase_text != expected_phrase:
                violations.append(f"Displayed phrase '{self.displayed_phrase_text}' doesn't match list phrase '{expected_phrase}' at index {self.current_phrase_index}")
        
        return violations


@dataclass
class UserState:
    """
    Model of what the user wants to do.
    This is the "user tracking state" - user's current intent.
    """
    # What the user wants to accomplish
    active_intents: Set[UserIntent] = field(default_factory=set)
    
    # What the user expects to see (oracle for testing)
    expected_visible: Set[UIElement] = field(default_factory=set)
    
    # User's perception - does reality match expectation?
    perception_matches: Optional[bool] = None
    perception_notes: str = ""
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary for logging/debugging"""
        return {
            'active_intents': [i.name for i in self.active_intents],
            'expected_visible': [e.name for e in self.expected_visible],
            'perception_matches': self.perception_matches,
            'perception_notes': self.perception_notes
        }


@dataclass
class CCSInteractionState:
    """
    Combined state representing both agents and their interaction.
    This is the complete "internal model" for testing.
    """
    app_state: AppState
    user_state: UserState
    
    # CCS port matching
    satisfied_interactions: Set[Tuple[UserIntent, AppCapability]] = field(default_factory=set)
    unsatisfied_user_intents: Set[UserIntent] = field(default_factory=set)
    unused_app_capabilities: Set[AppCapability] = field(default_factory=set)
    
    # Testing state
    test_step: int = 0
    bugs_found: List[Dict] = field(default_factory=list)
    
    # Timing information (Priority 2 improvement)
    timestamp: float = 0.0                    # Unix timestamp of this state
    time_since_last_transition: float = 0.0  # Seconds since previous transition
    
    def compute_port_matching(self):
        """
        Core CCS logic: Match user output ports with app input ports.
        Identifies satisfied interactions and unsatisfied ports.
        """
        # Define complementary port pairs (user intent -> app capability)
        port_pairs = {
            # Control interactions
            UserIntent.WANT_ENTER_TEXT: AppCapability.ACCEPT_TEXT_INPUT,
            UserIntent.WANT_RECORD_AUDIO: AppCapability.ACCEPT_AUDIO_RECORDING,
            UserIntent.WANT_UPLOAD_FILE: AppCapability.ACCEPT_FILE_UPLOAD,
            UserIntent.WANT_GO_PREVIOUS: AppCapability.ACCEPT_NAVIGATION_PREV,
            UserIntent.WANT_GO_NEXT: AppCapability.ACCEPT_NAVIGATION_NEXT,
            UserIntent.WANT_JUMP_TO_PHRASE: AppCapability.ACCEPT_JUMP_TO_PHRASE,
            UserIntent.WANT_TOGGLE_MODE: AppCapability.ACCEPT_MODE_TOGGLE,
            UserIntent.WANT_CLEAR_RECORDING: AppCapability.ACCEPT_CLEAR_RECORDING,
            UserIntent.WANT_CLEAR_LIST: AppCapability.ACCEPT_CLEAR_LIST,
            UserIntent.WANT_SEE_RESULTS: AppCapability.PROVIDE_ANALYSIS_RESULTS,
            
            # Audio playback interactions - specific types
            UserIntent.WANT_HEAR_TARGET_PRACTICE: AppCapability.PROVIDE_TARGET_AUDIO_PRACTICE,
            UserIntent.WANT_HEAR_USER_LIVE: AppCapability.PROVIDE_USER_AUDIO_LIVE,
            UserIntent.WANT_HEAR_TARGET_RESULTS: AppCapability.PROVIDE_TARGET_AUDIO_RESULTS,
            UserIntent.WANT_HEAR_USER_RESULTS: AppCapability.PROVIDE_USER_AUDIO_RESULTS,
            UserIntent.WANT_HEAR_RECOGNIZED: AppCapability.PROVIDE_RECOGNIZED_AUDIO,
            UserIntent.WANT_HEAR_PHONEME_CORRECT: AppCapability.PROVIDE_PHONEME_AUDIO_CORRECT,
            UserIntent.WANT_HEAR_PHONEME_USER: AppCapability.PROVIDE_PHONEME_AUDIO_USER,
        }
        
        self.satisfied_interactions.clear()
        self.unsatisfied_user_intents.clear()
        self.unused_app_capabilities.clear()
        
        # Match user intents with app capabilities
        for user_intent in self.user_state.active_intents:
            corresponding_capability = port_pairs.get(user_intent)
            if corresponding_capability and corresponding_capability in self.app_state.active_capabilities:
                self.satisfied_interactions.add((user_intent, corresponding_capability))
            else:
                self.unsatisfied_user_intents.add(user_intent)
        
        # Find unused app capabilities
        used_capabilities = {cap for _, cap in self.satisfied_interactions}
        self.unused_app_capabilities = self.app_state.active_capabilities - used_capabilities
    
    def check_ui_consistency(self) -> bool:
        """
        Testing oracle: Does the UI match what the model predicts?
        Returns True if user's perception matches expectation.
        """
        if self.user_state.perception_matches is None:
            return False  # User hasn't validated yet
        
        if not self.user_state.perception_matches:
            # Bug detected!
            bug_report = {
                'step': self.test_step,
                'type': 'UI_INCONSISTENCY',
                'expected_visible': [e.name for e in self.user_state.expected_visible],
                'actual_visible': [e.name for e in self.app_state.visible_elements],
                'notes': self.user_state.perception_notes
            }
            self.bugs_found.append(bug_report)
            return False
        
        return True
    
    def to_dict(self) -> Dict:
        """Full state snapshot for logging"""
        return {
            'test_step': self.test_step,
            'timestamp': self.timestamp,
            'time_since_last_transition': self.time_since_last_transition,
            'app_state': self.app_state.to_dict(),
            'user_state': self.user_state.to_dict(),
            'satisfied_interactions': [
                (ui.name, ac.name) for ui, ac in self.satisfied_interactions
            ],
            'unsatisfied_user_intents': [i.name for i in self.unsatisfied_user_intents],
            'unused_app_capabilities': [c.name for c in self.unused_app_capabilities],
            'bugs_found_count': len(self.bugs_found),
            'invariant_violations': self.app_state.check_invariants()
        }


class CCSTestOracle:
    """
    Testing oracle that tracks state transitions and validates consistency.
    """
    
    def __init__(self, test_config: Optional[Dict] = None):
        self.state_history: List[CCSInteractionState] = []
        self.current_state: Optional[CCSInteractionState] = None
        self.test_config: Dict = test_config or {}  # Store test configuration
    
    def initialize_state(self, mode: PracticeMode) -> CCSInteractionState:
        """Initialize a new testing session in given mode"""
        app_state = AppState(mode=mode)
        user_state = UserState()
        state = CCSInteractionState(app_state=app_state, user_state=user_state)
        
        self.current_state = state
        self.state_history.append(state)
        
        return state
    
    def transition(self, new_app_state: AppState, new_user_state: UserState) -> CCSInteractionState:
        """
        Record a state transition.
        This should be called whenever app state changes.
        """
        # Capture timing information
        current_time = time.time()
        time_since_last = 0.0
        if self.current_state is not None:
            time_since_last = current_time - self.current_state.timestamp
        
        state = CCSInteractionState(
            app_state=new_app_state,
            user_state=new_user_state,
            test_step=len(self.state_history),
            timestamp=current_time,
            time_since_last_transition=time_since_last
        )
        
        state.compute_port_matching()
        
        # Check invariants and log violations
        violations = new_app_state.check_invariants()
        if violations:
            # Automatically record as bug
            bug_report = {
                'step': state.test_step,
                'type': 'INVARIANT_VIOLATION',
                'violations': violations,
                'notes': 'Automated invariant check'
            }
            state.bugs_found.append(bug_report)
        
        self.current_state = state
        self.state_history.append(state)
        
        return state
    
    def user_validation(self, matches: bool, notes: str = ""):
        """
        User provides feedback: does the UI match expectations?
        This is the key testing mechanism.
        """
        if self.current_state:
            self.current_state.user_state.perception_matches = matches
            self.current_state.user_state.perception_notes = notes
            self.current_state.check_ui_consistency()
    
    def get_bugs(self) -> List[Dict]:
        """Retrieve all bugs found during testing"""
        all_bugs = []
        for state in self.state_history:
            all_bugs.extend(state.bugs_found)
        return all_bugs
    
    def save_test_session(self, filename: str):
        """Save complete test session to JSON for analysis"""
        session_data = {
            'test_config': self.test_config,  # Save test configuration
            'total_steps': len(self.state_history),
            'bugs_found': self.get_bugs(),
            'state_history': [state.to_dict() for state in self.state_history]
        }
        
        with open(filename, 'w') as f:
            json.dump(session_data, f, indent=2)
    
    def print_current_status(self):
        """Debug output: print current interaction state"""
        if not self.current_state:
            print("No current state")
            return
        
        print("\n" + "="*60)
        print(f"TEST STEP {self.current_state.test_step}")
        print("="*60)
        
        print(f"\nAPP STATE:")
        print(f"  Mode: {self.current_state.app_state.mode.name}")
        print(f"  Visible Elements: {len(self.current_state.app_state.visible_elements)}")
        for elem in sorted(self.current_state.app_state.visible_elements, key=lambda x: x.name):
            print(f"    - {elem.name}")
        
        print(f"\nUSER STATE:")
        print(f"  Active Intents: {len(self.current_state.user_state.active_intents)}")
        for intent in sorted(self.current_state.user_state.active_intents, key=lambda x: x.name):
            print(f"    - {intent.name}")
        
        print(f"\nPORT MATCHING:")
        print(f"  ✓ Satisfied: {len(self.current_state.satisfied_interactions)}")
        for ui, ac in self.current_state.satisfied_interactions:
            print(f"    {ui.name} <-> {ac.name}")
        
        print(f"  ✗ Unsatisfied User Intents: {len(self.current_state.unsatisfied_user_intents)}")
        for intent in self.current_state.unsatisfied_user_intents:
            print(f"    - {intent.name}")
        
        print(f"  ? Unused App Capabilities: {len(self.current_state.unused_app_capabilities)}")
        for cap in self.current_state.unused_app_capabilities:
            print(f"    - {cap.name}")
        
        if self.current_state.user_state.perception_matches is not None:
            match_str = "✓ MATCH" if self.current_state.user_state.perception_matches else "✗ MISMATCH"
            print(f"\nUSER PERCEPTION: {match_str}")
            if self.current_state.user_state.perception_notes:
                print(f"  Notes: {self.current_state.user_state.perception_notes}")
        
        print(f"\nBUGS FOUND: {len(self.current_state.bugs_found)}")
        print("="*60 + "\n")


# Example usage and helper functions
def build_free_text_state() -> AppState:
    """Build expected app state for free text mode"""
    state = AppState(mode=PracticeMode.FREE_TEXT)
    
    # Visible elements in free text mode
    state.visible_elements = {
        UIElement.TEXT_INPUT_FREE,
        UIElement.PHRASE_LIST_UPLOADER,
    }
    
    # Active capabilities
    state.active_capabilities = {
        AppCapability.ACCEPT_TEXT_INPUT,
        AppCapability.ACCEPT_FILE_UPLOAD,
    }
    
    return state


def build_guided_list_state(phrase_list: List[str], current_idx: int) -> AppState:
    """Build expected app state for guided list mode"""
    state = AppState(
        mode=PracticeMode.GUIDED_LIST,
        phrase_list=phrase_list,
        current_phrase_index=current_idx,
        current_text=phrase_list[current_idx] if phrase_list else None
    )
    
    # Visible elements in guided mode
    state.visible_elements = {
        UIElement.PHRASE_DISPLAY_BOLD,
        UIElement.PREV_BUTTON,
        UIElement.NEXT_BUTTON,
        UIElement.JUMP_SELECTOR,
        UIElement.EDIT_BUTTON,
        UIElement.PROGRESS_BAR,
        UIElement.PHRASE_LIST_UPLOADER,
    }
    
    # Active capabilities
    state.active_capabilities = {
        AppCapability.ACCEPT_NAVIGATION_PREV,
        AppCapability.ACCEPT_NAVIGATION_NEXT,
        AppCapability.ACCEPT_JUMP_TO_PHRASE,
        AppCapability.ACCEPT_MODE_TOGGLE,
        AppCapability.ACCEPT_FILE_UPLOAD,
    }
    
    return state


if __name__ == "__main__":
    # Example test scenario
    print("CCS Testing Framework - Example Session")
    print("This demonstrates the dual-agent model\n")
    
    oracle = CCSTestOracle()
    
    # Step 1: Start in free text mode
    print("STEP 1: Initialize in FREE_TEXT mode")
    app_state = build_free_text_state()
    user_state = UserState()
    user_state.active_intents = {UserIntent.WANT_ENTER_TEXT}
    user_state.expected_visible = {UIElement.TEXT_INPUT_FREE}
    
    oracle.transition(app_state, user_state)
    oracle.print_current_status()
    
    # User validates
    oracle.user_validation(matches=True, notes="Text input visible as expected")
    
    # Step 2: User uploads file
    print("\nSTEP 2: User uploads phrase list")
    app_state = build_guided_list_state(["Bom dia", "Obrigado", "Por favor"], 0)
    user_state = UserState()
    user_state.active_intents = {
        UserIntent.WANT_HEAR_TARGET_PRACTICE,  # Specific: hear target in practice area
        UserIntent.WANT_RECORD_AUDIO,
        UserIntent.WANT_GO_NEXT
    }
    user_state.expected_visible = {
        UIElement.PHRASE_DISPLAY_BOLD,
        UIElement.AUDIO_PLAYER_TARGET_PRACTICE,  # Specific audio player type
        UIElement.NEXT_BUTTON,
        UIElement.PREV_BUTTON
    }
    
    oracle.transition(app_state, user_state)
    oracle.print_current_status()
    
    # User validates - finds bug!
    oracle.user_validation(matches=False, notes="Phrase 'Bom dia' not showing in bold!")
    
    # Save session
    oracle.save_test_session("ccs_test_session.json")
    
    print("\n" + "="*60)
    print(f"TEST SESSION COMPLETE")
    print(f"Total bugs found: {len(oracle.get_bugs())}")
    print("="*60)
