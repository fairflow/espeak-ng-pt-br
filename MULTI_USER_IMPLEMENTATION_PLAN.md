# Multi-User Implementation Plan for Miolingo

**Version 1.3.0** | Created: 13 November 2025

## 🎯 Overview

This document outlines the implementation plan for adding secure multi-user support to Miolingo, enabling:
- User authentication and session management
- Per-user settings and customization
- Per-user, per-language progress tracking
- Spam/abuse prevention
- Modular architecture for future restructuring

## 📋 Requirements

### 1. User Authentication
- ✅ **Secure login/logout** with password hashing (bcrypt/argon2)
- ✅ **Session management** with secure tokens
- ✅ **User registration** with email validation
- ✅ **Password reset** functionality
- ✅ **OAuth options** (Google, GitHub) for future expansion

### 2. User Data Isolation
- ✅ **Per-user settings** (speech speed, pitch, voice, ASR model, etc.)
- ✅ **Per-user practice history** (isolated from other users)
- ✅ **Per-user, per-language progress** (Portuguese, French, Dutch separate)
- ✅ **User preferences** (UI theme, notifications, etc.)

### 3. Security & Anti-Abuse
- ✅ **Secure password storage** (no plaintext)
- ✅ **Rate limiting** on login attempts, practice submissions
- ✅ **CAPTCHA** for registration/login (optional but recommended)
- ✅ **Email verification** to prevent spam accounts
- ✅ **Session timeout** after inactivity
- ✅ **IP-based throttling** for API abuse prevention
- ✅ **User activity logging** for audit trails

### 4. Modular Architecture
- ✅ **Separate authentication module** (`app_auth.py`)
- ✅ **Database abstraction layer** (`app_database.py`)
- ✅ **User management module** (`app_user_manager.py`)
- ✅ **Minimal changes to core `app.py`**
- ✅ **Easy migration path** to full backend (Flask/FastAPI) if needed

## 🏗️ Architecture Design

### Current Architecture (v1.2.1)
```
app.py
├── Session state (st.session_state)
├── practice_config.json (global settings)
├── practice_history.json (global history)
└── app_language_materials.py (language materials)
```

**Issues:**
- All users share same settings
- All users share same practice history
- No user identification or isolation

### Proposed Architecture (v1.3.0)
```
app.py (main application)
├── app_auth.py (authentication & session management)
├── app_database.py (user data storage & retrieval)
├── app_user_manager.py (user CRUD operations)
└── user_data/
    ├── users.db (SQLite database)
    └── [user_id]/
        ├── settings.json (per-user settings)
        └── progress/
            ├── pt.json (Portuguese progress)
            ├── fr.json (French progress)
            └── nl.json (Dutch progress)
```

**Benefits:**
- Complete user data isolation
- Per-language progress tracking
- Secure credential storage
- Easy to migrate to PostgreSQL/MySQL later
- Modular components can be replaced independently

## 📦 Implementation Modules

### Module 1: `app_auth.py` - Authentication System

**Purpose:** Handle user authentication, session management, and security.

**Key Functions:**
```python
# User registration & login
def register_user(username: str, email: str, password: str) -> Dict
def login_user(username: str, password: str) -> Dict
def logout_user() -> None

# Session management
def get_current_user() -> Optional[Dict]
def is_authenticated() -> bool
def refresh_session() -> None

# Password management
def hash_password(password: str) -> str
def verify_password(password: str, hashed: str) -> bool
def reset_password(email: str) -> bool

# Security
def check_rate_limit(username: str, action: str) -> bool
def log_failed_attempt(username: str, ip: str) -> None
def is_session_valid() -> bool
```

**Security Features:**
- **Password Hashing:** Argon2id (recommended) or bcrypt
- **Session Tokens:** Cryptographically secure random tokens (32 bytes)
- **Rate Limiting:** Max 5 login attempts per 15 minutes per IP
- **Session Timeout:** 24 hours of inactivity
- **HTTPS Enforcement:** Streamlit Community Cloud provides this

**Streamlit Integration:**
```python
# Store auth state in st.session_state
st.session_state.auth = {
    "authenticated": False,
    "user_id": None,
    "username": None,
    "session_token": None,
    "last_activity": None
}
```

### Module 2: `app_database.py` - Data Storage Layer

**Purpose:** Abstract database operations for easy migration to different backends.

**Database Schema (SQLite):**
```sql
-- Users table
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    email_verified BOOLEAN DEFAULT 0,
    is_active BOOLEAN DEFAULT 1
);

-- Sessions table
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    ip_address TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Settings table (per-user)
CREATE TABLE user_settings (
    setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    setting_key TEXT NOT NULL,
    setting_value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    UNIQUE(user_id, setting_key)
);

-- Progress table (per-user, per-language)
CREATE TABLE user_progress (
    progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    language_code TEXT NOT NULL,  -- 'pt', 'fr', 'nl'
    practice_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    target_phrase TEXT NOT NULL,
    recognized_phrase TEXT NOT NULL,
    similarity_score REAL NOT NULL,
    perfect_match BOOLEAN NOT NULL,
    target_phonemes TEXT,
    user_phonemes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Rate limiting table
CREATE TABLE rate_limits (
    limit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    identifier TEXT NOT NULL,  -- username or IP
    action TEXT NOT NULL,       -- 'login', 'register', 'practice'
    attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_identifier_action (identifier, action)
);

-- Activity log (audit trail)
CREATE TABLE activity_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    details TEXT,
    ip_address TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

**Key Functions:**
```python
# Database initialization
def init_database() -> None
def migrate_database(version: str) -> None

# User CRUD
def create_user(username: str, email: str, password_hash: str) -> int
def get_user(user_id: int) -> Optional[Dict]
def get_user_by_username(username: str) -> Optional[Dict]
def get_user_by_email(email: str) -> Optional[Dict]
def update_user(user_id: int, updates: Dict) -> bool
def delete_user(user_id: int) -> bool

# Session management
def create_session(user_id: int, ip: str) -> str
def get_session(session_id: str) -> Optional[Dict]
def delete_session(session_id: str) -> bool
def cleanup_expired_sessions() -> int

# Settings management
def get_user_settings(user_id: int) -> Dict
def save_user_setting(user_id: int, key: str, value: Any) -> bool
def delete_user_setting(user_id: int, key: str) -> bool

# Progress tracking
def save_practice(user_id: int, language: str, practice_data: Dict) -> int
def get_user_progress(user_id: int, language: str, limit: int = 50) -> List[Dict]
def get_user_statistics(user_id: int, language: str) -> Dict

# Rate limiting
def check_rate_limit(identifier: str, action: str, max_attempts: int, window_minutes: int) -> bool
def log_rate_limit_attempt(identifier: str, action: str) -> None

# Activity logging
def log_activity(user_id: int, action: str, details: str, ip: str) -> None
```

### Module 3: `app_user_manager.py` - User Management

**Purpose:** High-level user management operations and business logic.

**Key Functions:**
```python
# User lifecycle
def register_new_user(username: str, email: str, password: str) -> Dict[str, Any]
def authenticate_user(username: str, password: str, ip: str) -> Dict[str, Any]
def get_user_profile(user_id: int) -> Dict
def update_user_profile(user_id: int, updates: Dict) -> bool

# Settings management
def load_user_settings(user_id: int) -> Dict
def save_user_settings(user_id: int, settings: Dict) -> bool
def reset_user_settings(user_id: int) -> bool

# Progress management
def save_practice_session(user_id: int, language: str, practices: List[Dict]) -> bool
def get_practice_history(user_id: int, language: str, limit: int = 100) -> List[Dict]
def get_user_stats(user_id: int, language: str) -> Dict
def get_all_language_stats(user_id: int) -> Dict[str, Dict]

# Security
def validate_password_strength(password: str) -> Dict[str, bool]
def send_verification_email(email: str, token: str) -> bool
def verify_email_token(token: str) -> Optional[int]
def initiate_password_reset(email: str) -> bool
def complete_password_reset(token: str, new_password: str) -> bool
```

### Module 4: Updated `app.py` - Main Application

**Changes Required:**

1. **Add authentication check at app start:**
```python
def main():
    initialize_session_state()
    
    # Check authentication
    if not is_authenticated():
        show_login_page()
        return
    
    # Get current user
    user = get_current_user()
    
    # Load user-specific settings and progress
    st.session_state.settings = load_user_settings(user['user_id'])
    st.session_state.history = get_practice_history(user['user_id'], st.session_state.language)
    
    # Continue with existing app logic...
```

2. **Replace global config files with user-specific data:**
```python
# OLD: practice_config.json (global)
def save_settings(settings: Dict):
    with open("practice_config.json", 'w') as f:
        json.dump(settings, f, indent=2)

# NEW: user-specific settings
def save_settings(settings: Dict):
    user = get_current_user()
    save_user_settings(user['user_id'], settings)
```

3. **Track practices per user, per language:**
```python
# OLD: practice_history.json (global)
def save_current_session():
    st.session_state.history.append(st.session_state.current_session)
    save_history(st.session_state.history)

# NEW: user-specific, language-specific
def save_current_session():
    user = get_current_user()
    language = st.session_state.language
    practices = st.session_state.current_sessions[language]["practices"]
    save_practice_session(user['user_id'], LANGUAGE_CONFIG[language]['code'], practices)
```

4. **Add logout button in sidebar:**
```python
with st.sidebar:
    st.markdown("---")
    st.write(f"👤 Logged in as: **{user['username']}**")
    if st.button("🚪 Logout"):
        logout_user()
        st.rerun()
```

## 🔒 Security Implementation Details

### 1. Password Security
- **Hashing Algorithm:** Argon2id (winner of Password Hashing Competition)
- **Salt:** Automatically generated per password
- **Memory Cost:** 65536 KB (64 MB)
- **Time Cost:** 3 iterations
- **Parallelism:** 4 threads

**Implementation:**
```python
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

def hash_password(password: str) -> str:
    """Hash password using Argon2id"""
    return ph.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    try:
        ph.verify(hashed, password)
        # Check if rehash needed (parameters changed)
        if ph.check_needs_rehash(hashed):
            return True, ph.hash(password)
        return True, None
    except VerifyMismatchError:
        return False, None
```

### 2. Session Management
- **Token Generation:** `secrets.token_urlsafe(32)` (256-bit security)
- **Storage:** SQLite sessions table
- **Expiration:** 24 hours from last activity
- **Renewal:** Auto-refresh on each request
- **Invalidation:** Logout or timeout

**Implementation:**
```python
import secrets
from datetime import datetime, timedelta

def create_session(user_id: int, ip: str) -> str:
    """Create new session for user"""
    session_id = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=24)
    
    db.execute("""
        INSERT INTO sessions (session_id, user_id, created_at, expires_at, ip_address)
        VALUES (?, ?, ?, ?, ?)
    """, (session_id, user_id, datetime.now(), expires_at, ip))
    
    return session_id

def is_session_valid(session_id: str) -> bool:
    """Check if session is valid and not expired"""
    session = db.query("""
        SELECT * FROM sessions 
        WHERE session_id = ? AND expires_at > ?
    """, (session_id, datetime.now()))
    
    return session is not None
```

### 3. Rate Limiting
- **Login Attempts:** Max 5 per 15 minutes per IP/username
- **Registration:** Max 3 per hour per IP
- **Practice Submissions:** Max 100 per hour per user (anti-spam)
- **Password Resets:** Max 3 per day per email

**Implementation:**
```python
def check_rate_limit(identifier: str, action: str, max_attempts: int, window_minutes: int) -> bool:
    """Check if action is within rate limit"""
    window_start = datetime.now() - timedelta(minutes=window_minutes)
    
    count = db.query("""
        SELECT COUNT(*) FROM rate_limits
        WHERE identifier = ? AND action = ? AND attempt_time > ?
    """, (identifier, action, window_start))
    
    if count >= max_attempts:
        return False
    
    # Log this attempt
    db.execute("""
        INSERT INTO rate_limits (identifier, action, attempt_time)
        VALUES (?, ?, ?)
    """, (identifier, action, datetime.now()))
    
    return True
```

### 4. Email Verification (Optional but Recommended)
- **Token:** Secure random token (32 bytes)
- **Expiration:** 24 hours
- **Resend:** Max 3 per hour
- **Service:** SendGrid, Mailgun, or SMTP

**Implementation:**
```python
import secrets

def send_verification_email(email: str, username: str) -> str:
    """Send email verification link"""
    token = secrets.token_urlsafe(32)
    expires = datetime.now() + timedelta(hours=24)
    
    # Store token in database
    db.execute("""
        INSERT INTO email_verifications (email, token, expires_at)
        VALUES (?, ?, ?)
    """, (email, token, expires))
    
    # Send email (pseudo-code)
    send_email(
        to=email,
        subject="Verify your Miolingo account",
        body=f"Click here to verify: https://miolingo.io/verify?token={token}"
    )
    
    return token
```

## 🚀 Migration Strategy

### Phase 1: Minimal Viable Authentication (Week 1)
1. ✅ Create `app_auth.py` with basic login/logout
2. ✅ Create `app_database.py` with SQLite backend
3. ✅ Create users table and sessions table
4. ✅ Add login page to `app.py`
5. ✅ Test with 2-3 test users

**Deliverable:** Users can register, login, and logout. Settings are still global.

### Phase 2: User-Specific Settings (Week 2)
1. ✅ Create `user_settings` table
2. ✅ Update `app.py` to load/save per-user settings
3. ✅ Migrate existing `practice_config.json` to user settings
4. ✅ Test settings isolation between users

**Deliverable:** Each user has their own settings (speed, pitch, model, etc.).

### Phase 3: User-Specific Progress (Week 3)
1. ✅ Create `user_progress` table
2. ✅ Update `app.py` to track per-user, per-language progress
3. ✅ Migrate existing `practice_history.json` to user progress
4. ✅ Add progress filtering by language
5. ✅ Test progress isolation and language separation

**Deliverable:** Each user has separate progress for each language.

### Phase 4: Security Hardening (Week 4)
1. ✅ Implement rate limiting
2. ✅ Add activity logging
3. ✅ Implement password strength validation
4. ✅ Add email verification (optional)
5. ✅ Security audit and penetration testing

**Deliverable:** Production-ready security features.

### Phase 5: Polish & Documentation (Week 5)
1. ✅ Add user profile page
2. ✅ Add password reset flow
3. ✅ Update USER_GUIDE.md with login instructions
4. ✅ Create ADMIN_GUIDE.md for user management
5. ✅ Load testing and optimization

**Deliverable:** v1.3.0 released with full multi-user support.

## 📊 Data Migration Plan

### Migrating Existing Data

**Scenario:** App is already in production with shared `practice_config.json` and `practice_history.json`.

**Solution:** Create "legacy user" account and migrate all existing data to it.

```python
def migrate_legacy_data():
    """Migrate shared data to legacy user account"""
    
    # 1. Create legacy user
    legacy_user_id = create_user(
        username="legacy_user",
        email="legacy@miolingo.io",
        password_hash=hash_password(secrets.token_urlsafe(32))  # Random password
    )
    
    # 2. Migrate settings
    if Path("practice_config.json").exists():
        with open("practice_config.json") as f:
            settings = json.load(f)
        for key, value in settings.items():
            save_user_setting(legacy_user_id, key, value)
    
    # 3. Migrate history
    if Path("practice_history.json").exists():
        with open("practice_history.json") as f:
            history = json.load(f)
        for session in history:
            # Infer language from practices (if possible)
            # Default to Portuguese if uncertain
            language = "pt"  # Default
            for practice in session.get("practices", []):
                save_practice(legacy_user_id, language, practice)
    
    # 4. Rename old files to .migrated
    Path("practice_config.json").rename("practice_config.json.migrated")
    Path("practice_history.json").rename("practice_history.json.migrated")
    
    print(f"✓ Migrated legacy data to user ID {legacy_user_id}")
```

## 🧪 Testing Strategy

### Unit Tests
```python
# test_app_auth.py
def test_password_hashing():
    password = "SecureP@ssw0rd123"
    hashed = hash_password(password)
    assert verify_password(password, hashed) == (True, None)
    assert verify_password("wrong", hashed) == (False, None)

def test_session_creation():
    session_id = create_session(user_id=1, ip="127.0.0.1")
    assert len(session_id) >= 32
    assert is_session_valid(session_id)

def test_rate_limiting():
    identifier = "test_user"
    action = "login"
    
    # Should allow first 5 attempts
    for i in range(5):
        assert check_rate_limit(identifier, action, 5, 15) == True
    
    # Should block 6th attempt
    assert check_rate_limit(identifier, action, 5, 15) == False
```

### Integration Tests
```python
# test_multi_user_flow.py
def test_user_isolation():
    # Create two users
    user1_id = register_new_user("alice", "alice@test.com", "pass123")
    user2_id = register_new_user("bob", "bob@test.com", "pass456")
    
    # Save different settings
    save_user_setting(user1_id, "speed", 120)
    save_user_setting(user2_id, "speed", 180)
    
    # Verify isolation
    user1_settings = get_user_settings(user1_id)
    user2_settings = get_user_settings(user2_id)
    
    assert user1_settings["speed"] == 120
    assert user2_settings["speed"] == 180
    assert user1_settings["speed"] != user2_settings["speed"]
```

### Load Tests
```python
# test_performance.py
def test_concurrent_logins():
    """Test 100 concurrent login attempts"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = [
            executor.submit(login_user, f"user{i}", f"pass{i}")
            for i in range(100)
        ]
        results = [f.result() for f in futures]
    
    # All should succeed (or fail due to invalid creds, not crashes)
    assert all(isinstance(r, dict) for r in results)
```

## 📈 Performance Considerations

### Database Optimization
1. **Indexes:**
   ```sql
   CREATE INDEX idx_username ON users(username);
   CREATE INDEX idx_email ON users(email);
   CREATE INDEX idx_session_user ON sessions(user_id);
   CREATE INDEX idx_progress_user_lang ON user_progress(user_id, language_code);
   CREATE INDEX idx_rate_limit_identifier ON rate_limits(identifier, action, attempt_time);
   ```

2. **Query Optimization:**
   - Use prepared statements (SQLite parameter substitution)
   - Limit result sets (e.g., last 50 practices)
   - Use pagination for large history views

3. **Connection Pooling:**
   ```python
   import sqlite3
   from contextlib import contextmanager
   
   @contextmanager
   def get_db_connection():
       conn = sqlite3.connect('user_data/users.db')
       conn.row_factory = sqlite3.Row
       try:
           yield conn
           conn.commit()
       finally:
           conn.close()
   ```

### Caching Strategy
```python
import streamlit as st
from functools import lru_cache

# Cache user settings in memory
@st.cache_data(ttl=300)  # 5 minutes
def get_cached_user_settings(user_id: int) -> Dict:
    return get_user_settings(user_id)

# Cache user stats
@st.cache_data(ttl=60)  # 1 minute
def get_cached_user_stats(user_id: int, language: str) -> Dict:
    return get_user_stats(user_id, language)
```

## 🌐 Future Enhancements

### v1.4.0: OAuth Integration
- Google OAuth
- GitHub OAuth
- Apple Sign In

### v1.5.0: Social Features
- Leaderboards (opt-in)
- Friend comparisons
- Shared progress badges

### v1.6.0: Admin Dashboard
- User management UI
- Analytics and metrics
- Content moderation tools

### v2.0.0: Backend Migration
- Migrate to FastAPI backend
- PostgreSQL database
- Redis caching layer
- Separate frontend (Next.js or continue with Streamlit)

## 📝 Code Review Checklist

Before merging multi-user code:

- [ ] All passwords are hashed (never stored in plaintext)
- [ ] Rate limiting is implemented on all auth endpoints
- [ ] Session tokens are cryptographically secure
- [ ] User data is properly isolated (no data leakage between users)
- [ ] SQL injection is prevented (parameterized queries only)
- [ ] XSS is prevented (Streamlit handles this, but verify user inputs)
- [ ] CSRF protection (session tokens in st.session_state)
- [ ] Activity logging is implemented for audit trails
- [ ] Error messages don't leak sensitive information
- [ ] All tests pass (unit, integration, load)
- [ ] Documentation is updated (USER_GUIDE, DEVELOPER_GUIDE)
- [ ] Migration script is tested on production-like data
- [ ] Rollback plan is documented
- [ ] Performance benchmarks are met (<200ms for auth, <500ms for queries)

## 🎉 Success Criteria

v1.3.0 is ready for production when:

1. ✅ 100+ concurrent users can login without issues
2. ✅ User data is completely isolated (verified by tests)
3. ✅ Rate limiting prevents brute-force attacks
4. ✅ Session management is secure and timeout works correctly
5. ✅ All existing features work identically for logged-in users
6. ✅ Performance is acceptable (<1s page load, <500ms queries)
7. ✅ Security audit passes (no critical vulnerabilities)
8. ✅ Documentation is complete and accurate
9. ✅ Migration from v1.2.1 is successful and reversible
10. ✅ User feedback is positive (beta testing with 10-20 users)

## 📞 Questions & Discussion

**Open Questions:**
1. Should we require email verification before allowing practice? (Prevents spam)
2. Should we implement "guest mode" (practice without account)? (Lower barrier to entry)
3. Should we add CAPTCHA on registration? (Prevents bot accounts)
4. Should we implement OAuth in v1.3.0 or wait for v1.4.0? (Faster to implement later)
5. Should we allow username changes? (Complications with references)

**Recommendations:**
- ✅ **Yes** to email verification (can be optional setting)
- ✅ **Yes** to guest mode (allow 5 practices before requiring login)
- ✅ **Yes** to CAPTCHA on registration (use hCaptcha, privacy-friendly)
- ⏳ **Later** for OAuth (focus on core auth first)
- ❌ **No** to username changes initially (keep it simple)

---

**Ready to implement?** Let's start with Phase 1 and iterate quickly! 🚀
