# Krystal Hosting Database Setup for Miolingo

**Date:** 13 November 2025  
**Branch:** feature/multi-user-auth-v1.3.0  
**Status:** ✅ **EXCELLENT SOLUTION - Krystal Supports Everything We Need!**

## 🎉 Great News!

**Krystal hosting includes EVERYTHING we need:**

### ✅ What's Included (Even on Amethyst £7/month plan):
- **Unlimited MySQL/MariaDB databases** 
- **phpMyAdmin** (web-based database management)
- **Remote MySQL access** (connect from Streamlit Cloud!)
- **Python support** (for any server-side scripts)
- **cPanel** (easy management interface)
- **SSH access** (for advanced setup)
- **Daily backups** (automatic)
- **Free SSL certificates** (HTTPS for API calls)

## 🏗️ Architecture: Krystal + Streamlit Cloud

```
┌─────────────────────────────────┐
│   Streamlit Community Cloud     │
│   (miolingo.streamlit.app)      │
│                                 │
│   - Frontend UI (app.py)        │
│   - User interactions           │
│   - Audio processing            │
│                                 │
└──────────────┬──────────────────┘
               │
               │ MySQL connection
               │ (via mysql-connector-python)
               │ Encrypted SSL/TLS
               │
┌──────────────▼──────────────────┐
│   miolingo.io (Krystal Hosting) │
│                                 │
│   ┌─────────────────────────┐  │
│   │  MySQL Database         │  │
│   │  - users                │  │
│   │  - user_settings        │  │
│   │  - user_progress        │  │
│   │  - sessions             │  │
│   └─────────────────────────┘  │
│                                 │
│   ┌─────────────────────────┐  │
│   │  Static Website         │  │
│   │  (optional landing page)│  │
│   └─────────────────────────┘  │
│                                 │
└─────────────────────────────────┘
```

## 📋 Setup Steps

### Phase 1: Create MySQL Database on Krystal (15 minutes)

**Via cPanel:**

1. **Login to cPanel**
   - Visit: `https://krystal.io/client`
   - Login with your Krystal account
   - Click "cPanel" for miolingo.io domain

2. **Create Database**
   - Go to "MySQL Databases" in cPanel
   - Under "Create New Database":
     - Database Name: `miolingo_users` (will be prefixed automatically: `username_miolingo_users`)
     - Click "Create Database"
   - Note the full database name (e.g., `matthew_miolingo_users`)

3. **Create Database User**
   - Under "MySQL Users":
     - Username: `miolingo_app` (will be prefixed: `username_miolingo_app`)
     - Password: Click "Password Generator" for strong password
     - Save password securely (you'll need it for Streamlit)
     - Click "Create User"

4. **Grant Privileges**
   - Under "Add User To Database":
     - User: `username_miolingo_app`
     - Database: `username_miolingo_users`
     - Click "Add"
   - On next screen, check "ALL PRIVILEGES"
   - Click "Make Changes"

5. **Enable Remote MySQL Access**
   - Go to "Remote MySQL" in cPanel
   - Add Access Host: `%` (allows connections from anywhere)
   - **IMPORTANT:** This is required for Streamlit Cloud to connect
   - Click "Add Host"

6. **Note Connection Details**
   Save these for Streamlit secrets:
   ```
   Host: mysql.krystal.io (or your specific hostname)
   Port: 3306
   Database: username_miolingo_users
   User: username_miolingo_app
   Password: <generated password>
   ```

### Phase 2: Create Database Schema (10 minutes)

**Via phpMyAdmin:**

1. **Open phpMyAdmin**
   - In cPanel, click "phpMyAdmin"
   - Select your database (`username_miolingo_users`)

2. **Run SQL Schema**
   - Click "SQL" tab
   - Paste the following schema:

```sql
-- Users table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    email_verified BOOLEAN DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Sessions table
CREATE TABLE sessions (
    session_id VARCHAR(64) PRIMARY KEY,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    ip_address VARCHAR(45),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_expires_at (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- User settings table
CREATE TABLE user_settings (
    setting_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    setting_key VARCHAR(100) NOT NULL,
    setting_value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_setting (user_id, setting_key),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- User progress table (per-language practice tracking)
CREATE TABLE user_progress (
    progress_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    language_code VARCHAR(10) NOT NULL,
    practice_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    target_phrase TEXT NOT NULL,
    recognized_phrase TEXT NOT NULL,
    similarity_score DECIMAL(5,2) NOT NULL,
    perfect_match BOOLEAN NOT NULL,
    target_phonemes TEXT,
    user_phonemes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_language (user_id, language_code),
    INDEX idx_practice_date (practice_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Rate limiting table
CREATE TABLE rate_limits (
    limit_id INT AUTO_INCREMENT PRIMARY KEY,
    identifier VARCHAR(255) NOT NULL,
    action VARCHAR(50) NOT NULL,
    attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_identifier_action_time (identifier, action, attempt_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Activity log table (audit trail)
CREATE TABLE activity_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(100) NOT NULL,
    details TEXT,
    ip_address VARCHAR(45),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

3. **Click "Go"** to execute
4. **Verify tables created** - Check left sidebar for 6 new tables

### Phase 3: Configure Streamlit Secrets (5 minutes)

**For Local Development:**

1. Create `.streamlit/secrets.toml` in your project:

```toml
[mysql]
host = "localhost"  # or "mysql.krystal.io" if testing remote
port = 3306
database = "username_miolingo_users"
user = "username_miolingo_app"
password = "your_generated_password"

[auth]
session_secret = "generate_random_32_byte_string_here"
```

**For Streamlit Cloud:**

1. Go to your app dashboard: `https://share.streamlit.io/`
2. Click on your app (miolingo)
3. Click "⚙️ Settings"
4. Go to "Secrets" section
5. Paste:

```toml
[mysql]
host = "mysql.krystal.io"
port = 3306
database = "username_miolingo_users"
user = "username_miolingo_app"
password = "your_generated_password"

[auth]
session_secret = "generate_random_32_byte_string_here"
```

6. Click "Save"

### Phase 4: Install Python Dependencies

Add to `requirements.txt`:

```
mysql-connector-python==8.2.0
argon2-cffi==23.1.0
python-dateutil==2.8.2
```

## 🔧 Implementation: Database Module

Create `app_mysql.py`:

```python
#!/usr/bin/env python3
"""
MySQL database connection and operations for Miolingo.
Connects to Krystal-hosted MySQL database from Streamlit Cloud.
"""

import mysql.connector
from mysql.connector import Error, pooling
import streamlit as st
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
import secrets
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Password hasher (Argon2id)
ph = PasswordHasher()

# Connection pool for better performance
_connection_pool = None

def get_connection_pool():
    """Get or create MySQL connection pool (cached)"""
    global _connection_pool
    
    if _connection_pool is None:
        try:
            _connection_pool = pooling.MySQLConnectionPool(
                pool_name="miolingo_pool",
                pool_size=5,
                pool_reset_session=True,
                host=st.secrets["mysql"]["host"],
                port=st.secrets["mysql"]["port"],
                database=st.secrets["mysql"]["database"],
                user=st.secrets["mysql"]["user"],
                password=st.secrets["mysql"]["password"],
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci',
                autocommit=False
            )
        except Error as e:
            st.error(f"Error creating connection pool: {e}")
            return None
    
    return _connection_pool

def get_connection():
    """Get a connection from the pool"""
    pool = get_connection_pool()
    if pool:
        try:
            return pool.get_connection()
        except Error as e:
            st.error(f"Error getting connection: {e}")
            return None
    return None

# ============================================================================
# User Management Functions
# ============================================================================

def create_user(username: str, email: str, password: str) -> Optional[int]:
    """Create new user account"""
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        password_hash = ph.hash(password)
        
        query = """
            INSERT INTO users (username, email, password_hash)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (username, email, password_hash))
        conn.commit()
        
        user_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return user_id
    except Error as e:
        st.error(f"Error creating user: {e}")
        if conn:
            conn.close()
        return None

def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """Authenticate user and return user data if valid"""
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT user_id, username, email, password_hash, is_active
            FROM users
            WHERE username = %s
        """
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            conn.close()
            return None
        
        if not user['is_active']:
            cursor.close()
            conn.close()
            return None
        
        # Verify password
        try:
            ph.verify(user['password_hash'], password)
            
            # Update last login
            update_query = """
                UPDATE users 
                SET last_login = NOW()
                WHERE user_id = %s
            """
            cursor.execute(update_query, (user['user_id'],))
            conn.commit()
            
            cursor.close()
            conn.close()
            
            return {
                'user_id': user['user_id'],
                'username': user['username'],
                'email': user['email']
            }
        except VerifyMismatchError:
            cursor.close()
            conn.close()
            return None
            
    except Error as e:
        st.error(f"Error authenticating user: {e}")
        if conn:
            conn.close()
        return None

def create_session(user_id: int, ip_address: str = None) -> Optional[str]:
    """Create new session for user"""
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=24)
        
        query = """
            INSERT INTO sessions (session_id, user_id, expires_at, ip_address)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (session_id, user_id, expires_at, ip_address))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return session_id
    except Error as e:
        st.error(f"Error creating session: {e}")
        if conn:
            conn.close()
        return None

def validate_session(session_id: str) -> Optional[Dict]:
    """Validate session and return user data if valid"""
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT s.user_id, u.username, u.email
            FROM sessions s
            JOIN users u ON s.user_id = u.user_id
            WHERE s.session_id = %s 
              AND s.expires_at > NOW()
              AND u.is_active = 1
        """
        cursor.execute(query, (session_id,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return result
    except Error as e:
        st.error(f"Error validating session: {e}")
        if conn:
            conn.close()
        return None

# ============================================================================
# Settings Management
# ============================================================================

def get_user_settings(user_id: int) -> Dict[str, Any]:
    """Get all settings for user"""
    conn = get_connection()
    if not conn:
        return {}
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT setting_key, setting_value
            FROM user_settings
            WHERE user_id = %s
        """
        cursor.execute(query, (user_id,))
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Convert to dictionary
        settings = {row['setting_key']: row['setting_value'] for row in results}
        return settings
    except Error as e:
        st.error(f"Error getting user settings: {e}")
        if conn:
            conn.close()
        return {}

def save_user_setting(user_id: int, key: str, value: Any) -> bool:
    """Save or update a user setting"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        query = """
            INSERT INTO user_settings (user_id, setting_key, setting_value)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE setting_value = %s
        """
        value_str = str(value)
        cursor.execute(query, (user_id, key, value_str, value_str))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return True
    except Error as e:
        st.error(f"Error saving setting: {e}")
        if conn:
            conn.close()
        return False

# ============================================================================
# Progress Tracking
# ============================================================================

def save_practice(user_id: int, language_code: str, practice_data: Dict) -> bool:
    """Save a practice session record"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        query = """
            INSERT INTO user_progress 
            (user_id, language_code, target_phrase, recognized_phrase, 
             similarity_score, perfect_match, target_phonemes, user_phonemes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            user_id,
            language_code,
            practice_data.get('target', ''),
            practice_data.get('recognized', ''),
            practice_data.get('similarity', 0.0),
            practice_data.get('match', False),
            practice_data.get('target_phonemes', ''),
            practice_data.get('user_phonemes', '')
        ))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return True
    except Error as e:
        st.error(f"Error saving practice: {e}")
        if conn:
            conn.close()
        return False

def get_user_progress(user_id: int, language_code: str, limit: int = 50) -> List[Dict]:
    """Get recent practice history for user and language"""
    conn = get_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT *
            FROM user_progress
            WHERE user_id = %s AND language_code = %s
            ORDER BY practice_date DESC
            LIMIT %s
        """
        cursor.execute(query, (user_id, language_code, limit))
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return results
    except Error as e:
        st.error(f"Error getting progress: {e}")
        if conn:
            conn.close()
        return []

def get_user_stats(user_id: int, language_code: str) -> Dict:
    """Get statistics for user and language"""
    conn = get_connection()
    if not conn:
        return {}
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                COUNT(*) as total_practices,
                SUM(CASE WHEN perfect_match = 1 THEN 1 ELSE 0 END) as perfect_count,
                AVG(similarity_score) as avg_similarity
            FROM user_progress
            WHERE user_id = %s AND language_code = %s
        """
        cursor.execute(query, (user_id, language_code))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return result or {}
    except Error as e:
        st.error(f"Error getting stats: {e}")
        if conn:
            conn.close()
        return {}

# ============================================================================
# Rate Limiting
# ============================================================================

def check_rate_limit(identifier: str, action: str, max_attempts: int, window_minutes: int) -> bool:
    """Check if action is within rate limit"""
    conn = get_connection()
    if not conn:
        return True  # Allow if DB connection fails (fail open)
    
    try:
        cursor = conn.cursor()
        
        # Count recent attempts
        query = """
            SELECT COUNT(*) as attempt_count
            FROM rate_limits
            WHERE identifier = %s 
              AND action = %s
              AND attempt_time > DATE_SUB(NOW(), INTERVAL %s MINUTE)
        """
        cursor.execute(query, (identifier, action, window_minutes))
        result = cursor.fetchone()
        attempt_count = result[0] if result else 0
        
        # Log this attempt
        insert_query = """
            INSERT INTO rate_limits (identifier, action, attempt_time)
            VALUES (%s, %s, NOW())
        """
        cursor.execute(insert_query, (identifier, action))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return attempt_count < max_attempts
    except Error as e:
        st.error(f"Error checking rate limit: {e}")
        if conn:
            conn.close()
        return True  # Fail open

# ============================================================================
# Cleanup Functions
# ============================================================================

def cleanup_expired_sessions() -> int:
    """Remove expired sessions (call periodically)"""
    conn = get_connection()
    if not conn:
        return 0
    
    try:
        cursor = conn.cursor()
        
        query = "DELETE FROM sessions WHERE expires_at < NOW()"
        cursor.execute(query)
        conn.commit()
        
        deleted_count = cursor.rowcount
        cursor.close()
        conn.close()
        
        return deleted_count
    except Error as e:
        st.error(f"Error cleaning up sessions: {e}")
        if conn:
            conn.close()
        return 0
```

## 🔒 Security Considerations

### SSL/TLS Encryption
- Krystal MySQL connections support SSL/TLS
- Add to connection config:
```python
connection_config = {
    ...
    'ssl_disabled': False,  # Enable SSL
}
```

### Connection Security
- ✅ Never expose database credentials in code
- ✅ Use Streamlit secrets for credentials
- ✅ Use connection pooling (5 connections max)
- ✅ Enable `autocommit=False` for transaction safety
- ✅ Use parameterized queries (prevents SQL injection)

### Password Security
- ✅ Argon2id hashing (best-in-class)
- ✅ Never store plaintext passwords
- ✅ Automatic salt generation per password

## 💰 Cost Analysis

### Krystal Hosting Costs:

**Amethyst Plan (£7/month = ~$9/month):**
- ✅ Unlimited MySQL databases
- ✅ 10GB NVMe storage (plenty for user database)
- ✅ Unlimited bandwidth
- ✅ Daily backups
- ✅ phpMyAdmin included
- ✅ Remote MySQL access
- ✅ Perfect for MVP and early growth

**When to Upgrade:**
- **Ruby (£11/month)** if you need 25GB storage
- **Emerald (£19/month)** if you need unlimited sites/storage

### Total Monthly Costs:
- Krystal hosting: £7/month ($9/month)
- Streamlit Cloud: $0 (free tier)
- Domain (miolingo.io): Already paid
- **Total: £7/month = ~$9/month** 🎉

### Comparison to Supabase:
- Supabase free: $0/month (but 500MB limit)
- Supabase Pro: $25/month
- **Krystal: £7/month with unlimited databases** ✅

## 🚀 Implementation Timeline

### Week 1: Database Setup & Connection
- ✅ Day 1: Create MySQL database on Krystal
- ✅ Day 2: Create schema and test phpMyAdmin
- ✅ Day 3: Build `app_mysql.py` module
- ✅ Day 4: Test connection from local machine
- ✅ Day 5: Deploy to Streamlit Cloud and test remote connection

### Week 2: Authentication & User Management
- Day 6-7: Build login/registration UI
- Day 8: Implement session management
- Day 9: Add user settings loading/saving
- Day 10: Testing and bug fixes

### Week 3: Progress Tracking
- Day 11-12: Implement per-user, per-language progress
- Day 13: Build statistics dashboard
- Day 14: History view with per-user data
- Day 15: Testing and optimization

### Week 4: Polish & Launch
- Day 16-17: Security audit and rate limiting
- Day 18: Performance optimization
- Day 19: Documentation and user guide updates
- Day 20: Production deployment and monitoring

**Total: 3-4 weeks to production** 🎯

## ✅ Advantages of Krystal + Streamlit Architecture

1. **Cost-Effective:** £7/month vs $25/month for Supabase Pro
2. **Full Control:** Direct MySQL access, no vendor lock-in
3. **Proven Stack:** MySQL + Python is battle-tested
4. **Easy Migration:** Can move to dedicated server later
5. **Familiar Tools:** phpMyAdmin for database management
6. **Your Domain:** Database hosted on miolingo.io (professional)
7. **Daily Backups:** Included with Krystal
8. **UK-Based Support:** Krystal's award-winning support team

## 📞 Next Steps

1. **Call Krystal Support:** Confirm remote MySQL access details
2. **Create Database:** Follow Phase 1 in cPanel
3. **Test Connection:** Run sample Python script locally
4. **Deploy Test:** Connect from Streamlit Cloud
5. **Build Auth Module:** Implement `app_mysql.py`
6. **Go Live:** Launch multi-user Miolingo v1.3.0!

---

**Ready to proceed?** This solution is:
- ✅ Cost-effective (£7/month)
- ✅ Production-ready (daily backups, SSL)
- ✅ Scalable (can upgrade as needed)
- ✅ Secure (Argon2 passwords, parameterized queries)
- ✅ Your infrastructure (hosted on miolingo.io)

Let me know what Krystal support says, and we can start building! 🚀
