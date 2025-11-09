"""
Integration layer between CCS testing framework and Streamlit app.

This module provides:
1. State extraction from Streamlit session_state
2. UI validation interface for users
3. Automated bug reporting
4. Test session management

Usage in streamlit_app_v2.py:
    from ccs_test_integration import CCSTestSession
    
    # Initialize (once at app start)
    if 'ccs_test' not in st.session_state:
        st.session_state.ccs_test = CCSTestSession()
    
    # Record state transitions
    st.session_state.ccs_test.capture_current_state()
    
    # Show validation UI
    st.session_state.ccs_test.render_validation_ui()
"""

import streamlit as st
from typing import Optional, Set
from ccs_test_framework import (
    CCSTestOracle, AppState, UserState, PracticeMode,
    UIElement, AppCapability, UserIntent
)


class CCSTestSession:
    """
    Manages CCS testing within a Streamlit app session.
    Provides methods to extract state from Streamlit and validate UI.
    """
    
    def __init__(self, enabled: bool = False):
        self.oracle = CCSTestOracle()
        self.enabled = enabled  # Can be toggled via UI
        self.auto_capture = False  # If True, captures state on every rerun
    
    def extract_app_state_from_streamlit(self) -> AppState:
        """
        Extract current app state from Streamlit session_state.
        This is the key bridge between actual app and testing model.
        """
        # Determine mode
        if 'phrase_list' in st.session_state and st.session_state.get('phrase_list'):
            if st.session_state.get('edit_mode', False):
                mode = PracticeMode.GUIDED_EDIT
            else:
                mode = PracticeMode.GUIDED_LIST
        else:
            mode = PracticeMode.FREE_TEXT
        
        # Create app state
        app_state = AppState(mode=mode)
        
        # Extract data state
        app_state.current_text = st.session_state.get('practice_text', None)
        app_state.phrase_list = st.session_state.get('phrase_list', [])
        app_state.current_phrase_index = st.session_state.get('current_phrase_index', 0)
        app_state.has_recording = st.session_state.get('last_result', None) is not None
        app_state.has_results = st.session_state.get('last_result', None) is not None
        
        # Infer visible elements based on mode
        app_state.visible_elements = self._infer_visible_elements(app_state)
        
        # Infer active capabilities
        app_state.active_capabilities = self._infer_capabilities(app_state)
        
        return app_state
    
    def _infer_visible_elements(self, app_state: AppState) -> Set[UIElement]:
        """
        Infer which UI elements should be visible based on app state.
        This encodes our expectations about the UI.
        """
        visible = set()
        
        # Always visible
        visible.add(UIElement.PHRASE_LIST_UPLOADER)
        
        if app_state.mode == PracticeMode.FREE_TEXT:
            visible.add(UIElement.TEXT_INPUT_FREE)
            
        elif app_state.mode == PracticeMode.GUIDED_LIST:
            visible.add(UIElement.PHRASE_DISPLAY_BOLD)
            visible.add(UIElement.PREV_BUTTON)
            visible.add(UIElement.NEXT_BUTTON)
            visible.add(UIElement.JUMP_SELECTOR)
            visible.add(UIElement.EDIT_BUTTON)
            visible.add(UIElement.PROGRESS_BAR)
            visible.add(UIElement.CLEAR_LIST_BUTTON)
            
        elif app_state.mode == PracticeMode.GUIDED_EDIT:
            visible.add(UIElement.TEXT_INPUT_EDIT)
            visible.add(UIElement.BACK_TO_LIST_BUTTON)
            visible.add(UIElement.PREV_BUTTON)
            visible.add(UIElement.NEXT_BUTTON)
            visible.add(UIElement.JUMP_SELECTOR)
            visible.add(UIElement.PROGRESS_BAR)
        
        # Conditional elements based on state
        if app_state.current_text:
            visible.add(UIElement.TARGET_AUDIO_PLAYER)
            visible.add(UIElement.AUDIO_RECORDER)
        
        if app_state.has_recording:
            visible.add(UIElement.USER_AUDIO_PLAYER)
            visible.add(UIElement.CHECK_BUTTON)
            visible.add(UIElement.CLEAR_BUTTON)
        
        if app_state.has_results:
            visible.add(UIElement.RESULTS_PANEL)
        
        return visible
    
    def _infer_capabilities(self, app_state: AppState) -> Set[AppCapability]:
        """
        Infer which capabilities the app should offer based on state.
        """
        capabilities = set()
        
        # Always available
        capabilities.add(AppCapability.ACCEPT_FILE_UPLOAD)
        
        if app_state.mode == PracticeMode.FREE_TEXT:
            capabilities.add(AppCapability.ACCEPT_TEXT_INPUT)
            
        elif app_state.mode == PracticeMode.GUIDED_LIST:
            if app_state.current_phrase_index > 0:
                capabilities.add(AppCapability.ACCEPT_NAVIGATION_PREV)
            if app_state.current_phrase_index < len(app_state.phrase_list) - 1:
                capabilities.add(AppCapability.ACCEPT_NAVIGATION_NEXT)
            if len(app_state.phrase_list) > 1:
                capabilities.add(AppCapability.ACCEPT_JUMP_TO_PHRASE)
            capabilities.add(AppCapability.ACCEPT_MODE_TOGGLE)
            capabilities.add(AppCapability.ACCEPT_CLEAR_LIST)
            
        elif app_state.mode == PracticeMode.GUIDED_EDIT:
            capabilities.add(AppCapability.ACCEPT_TEXT_INPUT)
            capabilities.add(AppCapability.ACCEPT_MODE_TOGGLE)
        
        # Conditional capabilities
        if app_state.current_text:
            capabilities.add(AppCapability.PROVIDE_TARGET_AUDIO)
            capabilities.add(AppCapability.ACCEPT_AUDIO_RECORDING)
        
        if app_state.has_recording:
            capabilities.add(AppCapability.ACCEPT_CLEAR_RECORDING)
        
        if app_state.has_results:
            capabilities.add(AppCapability.PROVIDE_ANALYSIS_RESULTS)
        
        return capabilities
    
    def capture_current_state(self, user_intents: Optional[Set[UserIntent]] = None):
        """
        Capture current app state and record transition.
        Call this after any significant app state change.
        """
        if not self.enabled:
            return
        
        app_state = self.extract_app_state_from_streamlit()
        
        # Create user state (can be updated via UI)
        user_state = UserState()
        if user_intents:
            user_state.active_intents = user_intents
        
        # Record transition
        self.oracle.transition(app_state, user_state)
    
    def render_validation_ui(self):
        """
        Render UI for user to validate whether displayed UI matches expectations.
        This is the testing oracle interface.
        """
        if not self.enabled:
            return
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("🧪 CCS Testing")
        
        if st.sidebar.button("📊 Show Current State"):
            if self.oracle.current_state:
                with st.sidebar.expander("Current Test State", expanded=True):
                    state_dict = self.oracle.current_state.to_dict()
                    st.json(state_dict)
        
        st.sidebar.markdown("**UI Validation:**")
        st.sidebar.caption("Does what you see match the model?")
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("✅ Matches", key="validate_yes"):
                self.oracle.user_validation(matches=True)
                st.success("Validated!")
        with col2:
            if st.button("❌ Mismatch", key="validate_no"):
                notes = st.text_area("What's wrong?", key="validation_notes")
                self.oracle.user_validation(matches=False, notes=notes)
                st.error("Bug recorded!")
        
        # Show bugs found
        bugs = self.oracle.get_bugs()
        if bugs:
            st.sidebar.markdown(f"**🐛 Bugs Found: {len(bugs)}**")
            with st.sidebar.expander("View Bugs"):
                for i, bug in enumerate(bugs, 1):
                    st.markdown(f"**Bug #{i}** (Step {bug['step']})")
                    st.markdown(f"Type: {bug['type']}")
                    st.markdown(f"Notes: {bug['notes']}")
                    st.markdown("---")
        
        # Save session button
        if st.sidebar.button("💾 Save Test Session"):
            filename = f"ccs_test_session_{st.session_state.get('test_session_id', 'default')}.json"
            self.oracle.save_test_session(filename)
            st.sidebar.success(f"Saved to {filename}")
    
    def render_toggle_ui(self):
        """
        Render UI to enable/disable testing mode.
        Put this in the sidebar settings.
        """
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔬 Testing Mode")
        
        self.enabled = st.sidebar.checkbox(
            "Enable CCS Testing",
            value=self.enabled,
            help="Enable CCS-based testing framework to track state and find bugs"
        )
        
        if self.enabled:
            self.auto_capture = st.sidebar.checkbox(
                "Auto-capture state",
                value=self.auto_capture,
                help="Automatically capture state on every rerun (verbose)"
            )
            
            st.sidebar.info(
                "🧪 Testing mode active! Validate UI at each step using "
                "the controls below."
            )


def create_user_intent_selector() -> Set[UserIntent]:
    """
    Helper to let user specify their current intents for testing.
    Returns selected intents.
    """
    st.sidebar.markdown("**What do you want to do?**")
    
    intents = set()
    
    if st.sidebar.checkbox("Enter/edit text", key="intent_text"):
        intents.add(UserIntent.WANT_ENTER_TEXT)
    if st.sidebar.checkbox("Record audio", key="intent_record"):
        intents.add(UserIntent.WANT_RECORD_AUDIO)
    if st.sidebar.checkbox("Upload file", key="intent_upload"):
        intents.add(UserIntent.WANT_UPLOAD_FILE)
    if st.sidebar.checkbox("Navigate (prev/next)", key="intent_nav"):
        intents.add(UserIntent.WANT_GO_PREVIOUS)
        intents.add(UserIntent.WANT_GO_NEXT)
    if st.sidebar.checkbox("Jump to phrase", key="intent_jump"):
        intents.add(UserIntent.WANT_JUMP_TO_PHRASE)
    if st.sidebar.checkbox("Toggle mode", key="intent_mode"):
        intents.add(UserIntent.WANT_TOGGLE_MODE)
    if st.sidebar.checkbox("Clear recording", key="intent_clear"):
        intents.add(UserIntent.WANT_CLEAR_RECORDING)
    if st.sidebar.checkbox("Hear target", key="intent_hear"):
        intents.add(UserIntent.WANT_HEAR_TARGET)
    if st.sidebar.checkbox("See results", key="intent_results"):
        intents.add(UserIntent.WANT_SEE_RESULTS)
    
    return intents


# Example integration snippet for streamlit_app_v2.py
"""
# Add to imports:
from ccs_test_integration import CCSTestSession

# Add to initialize_session_state():
if 'ccs_test' not in st.session_state:
    st.session_state.ccs_test = CCSTestSession(enabled=False)

# Add to sidebar (in settings area):
st.session_state.ccs_test.render_toggle_ui()
if st.session_state.ccs_test.enabled:
    st.session_state.ccs_test.render_validation_ui()

# Add after state changes (e.g., after button clicks):
if st.session_state.ccs_test.enabled and st.session_state.ccs_test.auto_capture:
    st.session_state.ccs_test.capture_current_state()
"""
