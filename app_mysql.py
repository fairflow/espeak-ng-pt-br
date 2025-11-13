"""
Miolingo MySQL Database Module
Handles all database operations for multi-user authentication and progress tracking.

Security features:
- Argon2id password hashing (hardened for Emerald plan)
- Parameterized queries (SQL injection prevention)
- Connection pooling (optimized for Emerald resources)
- Session management with expiration
- Rate limiting support
- Audit logging

Author: Miolingo Team
Version: 1.3.0
"""

import streamlit as st
import mysql.connector
from mysql.connector import pooling, Error
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple
import json


# ============================================================================
# PASSWORD HASHING (Hardened for Emerald Plan)
# ============================================================================

# Argon2id password hasher - memory-hard, GPU-resistant
# Parameters optimized for Emerald plan resources
pwd_hasher = PasswordHasher(
    time_cost=4,        # 4 iterations (hardened from default 3)
    memory_cost=102400, # 100 MB per hash (hardened from default 64 MB)
    parallelism=8,      # 8 threads (hardened from default 4)
    hash_len=32,        # 32-byte hash output
    salt_len=16         # 16-byte random salt per password
)


# ============================================================================
# CONNECTION POOLING (Optimized for Emerald Plan)
# ============================================================================

_connection_pool = None

def get_connection_pool() -> pooling.MySQLConnectionPool:
    """
    Get or create MySQL connection pool.
    Connection pooling improves performance by reusing database connections.
    Emerald plan resources allow for higher concurrency.
    """
    global _connection_pool
    
    if _connection_pool is None:
        try:
            _connection_pool = pooling.MySQLConnectionPool(
                pool_name="miolingo_pool",
                pool_size=10,  # Increased for Emerald plan resources
                pool_reset_session=True,
                host=st.secrets["mysql"]["host"],
                port=st.secrets["mysql"]["port"],
                database=st.secrets["mysql"]["database"],
                user=st.secrets["mysql"]["user"],
                password=st.secrets["mysql"]["password"],
                autocommit=False,  # Explicit transaction control
                connection_timeout=10
            )
        except Error as e:
            st.error(f"❌ Database connection pool failed: {e}")
            raise
    
    return _connection_pool


def get_connection() -> mysql.connector.MySQLConnection:
    """
    Get a connection from the pool.
    Always use with try/finally to ensure connection is returned to pool.
    """
    pool = get_connection_pool()
    return pool.get_connection()


# ============================================================================
# USER MANAGEMENT
# ============================================================================

def create_user(username: str, email: str, password: str) -> Optional[int]:
    """
    Create a new user account.
    
    Args:
        username: Unique username (3-20 chars, alphanumeric)
        email: Unique email address
        password: Plain text password (will be hashed with Argon2id)
    
    Returns:
        user_id if successful, None if failed
    """
    conn = None
    try:
        # Hash password with Argon2id
        password_hash = pwd_hasher.hash(password)
        
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO users (username, email, password_hash, created_at, is_active)
            VALUES (%s, %s, %s, NOW(), TRUE)
        """
        cursor.execute(query, (username, email, password_hash))
        conn.commit()
        
        user_id = cursor.lastrowid
        cursor.close()
        
        # Log account creation
        log_activity(user_id, "USER_CREATED", f"Username: {username}, Email: {email}", "system")
        
        return user_id
        
    except Error as e:
        if conn:
            conn.rollback()
        
        # Check for duplicate username/email
        if "Duplicate entry" in str(e):
            if "username" in str(e):
                st.error("❌ Username already exists. Please choose another.")
            elif "email" in str(e):
                st.error("❌ Email already registered. Please use another or login.")
        else:
            st.error(f"❌ Failed to create user: {e}")
        
        return None
    
    finally:
        if conn:
            conn.close()


def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """
    Authenticate user with username and password.
    
    Args:
        username: Username
        password: Plain text password
    
    Returns:
        User dict {user_id, username, email} if successful, None if failed
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT user_id, username, email, password_hash, is_active
            FROM users
            WHERE username = %s
        """
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        cursor.close()
        
        if not user:
            log_activity(None, "LOGIN_FAILED", f"Username not found: {username}", "system")
            return None
        
        if not user['is_active']:
            log_activity(user['user_id'], "LOGIN_FAILED", "Account inactive", "system")
            st.error("❌ Account is inactive. Please contact support.")
            return None
        
        # Verify password with Argon2id
        try:
            pwd_hasher.verify(user['password_hash'], password)
            
            # Update last login
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET last_login = NOW() WHERE user_id = %s", (user['user_id'],))
            conn.commit()
            cursor.close()
            
            # Log successful login
            log_activity(user['user_id'], "LOGIN_SUCCESS", f"Username: {username}", "system")
            
            return {
                'user_id': user['user_id'],
                'username': user['username'],
                'email': user['email']
            }
            
        except VerifyMismatchError:
            log_activity(user['user_id'], "LOGIN_FAILED", "Invalid password", "system")
            return None
    
    except Error as e:
        st.error(f"❌ Authentication error: {e}")
        return None
    
    finally:
        if conn:
            conn.close()


def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Get user details by user_id."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT user_id, username, email, created_at, last_login FROM users WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        cursor.close()
        
        return user
    
    except Error as e:
        st.error(f"❌ Error fetching user: {e}")
        return None
    
    finally:
        if conn:
            conn.close()


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

def create_session(user_id: int, ip_address: str = "unknown") -> Optional[str]:
    """
    Create a new session for authenticated user.
    
    Args:
        user_id: User ID
        ip_address: Client IP address for security tracking
    
    Returns:
        session_id (32-byte secure token) if successful, None if failed
    """
    conn = None
    try:
        # Generate cryptographically secure session ID
        session_id = secrets.token_urlsafe(32)
        
        # Session expires in 24 hours
        expires_at = datetime.now() + timedelta(hours=24)
        
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO sessions (session_id, user_id, created_at, expires_at, ip_address)
            VALUES (%s, %s, NOW(), %s, %s)
        """
        cursor.execute(query, (session_id, user_id, expires_at, ip_address))
        conn.commit()
        cursor.close()
        
        log_activity(user_id, "SESSION_CREATED", f"IP: {ip_address}", ip_address)
        
        return session_id
        
    except Error as e:
        if conn:
            conn.rollback()
        st.error(f"❌ Failed to create session: {e}")
        return None
    
    finally:
        if conn:
            conn.close()


def validate_session(session_id: str, ip_address: str = "unknown") -> Optional[Dict]:
    """
    Validate session and return user info.
    Also checks IP address for session hijacking detection.
    
    Args:
        session_id: Session token
        ip_address: Current client IP address
    
    Returns:
        User dict if session valid, None if invalid/expired
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT s.session_id, s.user_id, s.ip_address, s.expires_at,
                   u.username, u.email, u.is_active
            FROM sessions s
            JOIN users u ON s.user_id = u.user_id
            WHERE s.session_id = %s AND s.expires_at > NOW()
        """
        cursor.execute(query, (session_id,))
        session = cursor.fetchone()
        cursor.close()
        
        if not session:
            return None
        
        # Check if user is active
        if not session['is_active']:
            return None
        
        # IP address validation (detect session hijacking)
        if session['ip_address'] != ip_address and session['ip_address'] != "unknown":
            log_activity(
                session['user_id'],
                "SESSION_IP_MISMATCH",
                f"Expected: {session['ip_address']}, Got: {ip_address}",
                ip_address
            )
            # Still allow (IPs can change legitimately), but log for security monitoring
        
        return {
            'user_id': session['user_id'],
            'username': session['username'],
            'email': session['email']
        }
        
    except Error as e:
        st.error(f"❌ Session validation error: {e}")
        return None
    
    finally:
        if conn:
            conn.close()


def delete_session(session_id: str) -> bool:
    """Delete a session (logout)."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get user_id before deleting
        cursor.execute("SELECT user_id FROM sessions WHERE session_id = %s", (session_id,))
        result = cursor.fetchone()
        user_id = result[0] if result else None
        
        cursor.execute("DELETE FROM sessions WHERE session_id = %s", (session_id,))
        conn.commit()
        cursor.close()
        
        if user_id:
            log_activity(user_id, "SESSION_DELETED", "User logged out", "system")
        
        return True
        
    except Error as e:
        if conn:
            conn.rollback()
        st.error(f"❌ Failed to delete session: {e}")
        return False
    
    finally:
        if conn:
            conn.close()


def cleanup_expired_sessions() -> int:
    """
    Remove expired sessions from database.
    Should be run periodically (e.g., daily cron job).
    
    Returns:
        Number of sessions deleted
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM sessions WHERE expires_at < NOW()")
        deleted_count = cursor.rowcount
        conn.commit()
        cursor.close()
        
        return deleted_count
        
    except Error as e:
        if conn:
            conn.rollback()
        return 0
    
    finally:
        if conn:
            conn.close()


# ============================================================================
# USER SETTINGS (Per-User Configuration)
# ============================================================================

def get_user_settings(user_id: int) -> Dict[str, Any]:
    """
    Get all settings for a user as a dictionary.
    
    Args:
        user_id: User ID
    
    Returns:
        Dict of {setting_key: setting_value}
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT setting_key, setting_value FROM user_settings WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        cursor.close()
        
        # Convert to dict and deserialize JSON values
        settings = {}
        for row in rows:
            try:
                settings[row['setting_key']] = json.loads(row['setting_value'])
            except json.JSONDecodeError:
                settings[row['setting_key']] = row['setting_value']
        
        return settings
        
    except Error as e:
        st.error(f"❌ Error fetching settings: {e}")
        return {}
    
    finally:
        if conn:
            conn.close()


def save_user_setting(user_id: int, key: str, value: Any) -> bool:
    """
    Save a single setting for a user.
    Uses INSERT ... ON DUPLICATE KEY UPDATE for upsert behavior.
    
    Args:
        user_id: User ID
        key: Setting key (e.g., "language", "voice_variant")
        value: Setting value (will be JSON serialized)
    
    Returns:
        True if successful, False otherwise
    """
    conn = None
    try:
        # Serialize value to JSON
        value_json = json.dumps(value)
        
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO user_settings (user_id, setting_key, setting_value, updated_at)
            VALUES (%s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE setting_value = %s, updated_at = NOW()
        """
        cursor.execute(query, (user_id, key, value_json, value_json))
        conn.commit()
        cursor.close()
        
        return True
        
    except Error as e:
        if conn:
            conn.rollback()
        st.error(f"❌ Failed to save setting: {e}")
        return False
    
    finally:
        if conn:
            conn.close()


def delete_user_setting(user_id: int, key: str) -> bool:
    """Delete a specific setting for a user."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = "DELETE FROM user_settings WHERE user_id = %s AND setting_key = %s"
        cursor.execute(query, (user_id, key))
        conn.commit()
        cursor.close()
        
        return True
        
    except Error as e:
        if conn:
            conn.rollback()
        st.error(f"❌ Failed to delete setting: {e}")
        return False
    
    finally:
        if conn:
            conn.close()


# ============================================================================
# PRACTICE PROGRESS (Per-User, Per-Language Tracking)
# ============================================================================

def save_practice(
    user_id: int,
    language_code: str,
    target_phrase: str,
    recognized_phrase: str,
    similarity_score: float,
    perfect_match: bool,
    target_phonemes: str = "",
    user_phonemes: str = ""
) -> bool:
    """
    Save a practice session result.
    
    Args:
        user_id: User ID
        language_code: Language code (e.g., "pt-BR", "fr-FR")
        target_phrase: Original phrase to practice
        recognized_phrase: What the user said (from speech recognition)
        similarity_score: Similarity score (0-100)
        perfect_match: Whether it was a perfect match
        target_phonemes: Target phoneme representation
        user_phonemes: User's phoneme representation
    
    Returns:
        True if successful, False otherwise
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO user_progress (
                user_id, language_code, practice_date,
                target_phrase, recognized_phrase, similarity_score, perfect_match,
                target_phonemes, user_phonemes
            ) VALUES (%s, %s, NOW(), %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            user_id, language_code, target_phrase, recognized_phrase,
            similarity_score, perfect_match, target_phonemes, user_phonemes
        ))
        conn.commit()
        cursor.close()
        
        return True
        
    except Error as e:
        if conn:
            conn.rollback()
        st.error(f"❌ Failed to save practice: {e}")
        return False
    
    finally:
        if conn:
            conn.close()


def get_user_progress(user_id: int, language_code: str, limit: int = 50) -> List[Dict]:
    """
    Get recent practice history for a user and language.
    
    Args:
        user_id: User ID
        language_code: Language code (e.g., "pt-BR")
        limit: Maximum number of records to return
    
    Returns:
        List of practice session dicts
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT progress_id, language_code, practice_date,
                   target_phrase, recognized_phrase, similarity_score, perfect_match,
                   target_phonemes, user_phonemes
            FROM user_progress
            WHERE user_id = %s AND language_code = %s
            ORDER BY practice_date DESC
            LIMIT %s
        """
        cursor.execute(query, (user_id, language_code, limit))
        progress = cursor.fetchall()
        cursor.close()
        
        return progress
        
    except Error as e:
        st.error(f"❌ Error fetching progress: {e}")
        return []
    
    finally:
        if conn:
            conn.close()


def get_user_stats(user_id: int, language_code: str) -> Dict:
    """
    Get statistics for a user's practice in a specific language.
    
    Args:
        user_id: User ID
        language_code: Language code
    
    Returns:
        Dict with statistics: {total, perfect_count, avg_score, recent_avg}
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN perfect_match = 1 THEN 1 ELSE 0 END) as perfect_count,
                AVG(similarity_score) as avg_score
            FROM user_progress
            WHERE user_id = %s AND language_code = %s
        """
        cursor.execute(query, (user_id, language_code))
        stats = cursor.fetchone()
        
        # Get average of last 10 practices
        query_recent = """
            SELECT AVG(similarity_score) as recent_avg
            FROM (
                SELECT similarity_score 
                FROM user_progress
                WHERE user_id = %s AND language_code = %s
                ORDER BY practice_date DESC
                LIMIT 10
            ) recent
        """
        cursor.execute(query_recent, (user_id, language_code))
        recent = cursor.fetchone()
        
        cursor.close()
        
        return {
            'total': stats['total'] or 0,
            'perfect_count': stats['perfect_count'] or 0,
            'avg_score': float(stats['avg_score'] or 0),
            'recent_avg': float(recent['recent_avg'] or 0)
        }
        
    except Error as e:
        st.error(f"❌ Error fetching stats: {e}")
        return {'total': 0, 'perfect_count': 0, 'avg_score': 0, 'recent_avg': 0}
    
    finally:
        if conn:
            conn.close()


# ============================================================================
# RATE LIMITING
# ============================================================================

def check_rate_limit(
    identifier: str,
    action: str,
    max_attempts: int,
    window_minutes: int
) -> bool:
    """
    Check if action is rate-limited.
    
    Args:
        identifier: User ID, IP address, or email
        action: Action type (e.g., "LOGIN_ATTEMPT", "PRACTICE_SUBMIT")
        max_attempts: Maximum attempts allowed
        window_minutes: Time window in minutes
    
    Returns:
        True if allowed, False if rate limit exceeded
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
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
        
        if result['attempt_count'] >= max_attempts:
            cursor.close()
            return False
        
        # Log this attempt
        insert_query = """
            INSERT INTO rate_limits (identifier, action, attempt_time)
            VALUES (%s, %s, NOW())
        """
        cursor.execute(insert_query, (identifier, action))
        conn.commit()
        cursor.close()
        
        return True
        
    except Error as e:
        if conn:
            conn.rollback()
        # On error, allow the action (fail open)
        return True
    
    finally:
        if conn:
            conn.close()


# ============================================================================
# ACTIVITY LOGGING (Audit Trail)
# ============================================================================

def log_activity(
    user_id: Optional[int],
    action: str,
    details: str,
    ip_address: str = "system"
) -> bool:
    """
    Log user activity for audit trail.
    
    Args:
        user_id: User ID (None for system events)
        action: Action type (e.g., "LOGIN_SUCCESS", "SETTING_CHANGED")
        details: Additional details
        ip_address: Client IP address
    
    Returns:
        True if logged successfully
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO activity_log (user_id, action, details, ip_address, timestamp)
            VALUES (%s, %s, %s, %s, NOW())
        """
        cursor.execute(query, (user_id, action, details, ip_address))
        conn.commit()
        cursor.close()
        
        return True
        
    except Error as e:
        if conn:
            conn.rollback()
        # Don't show error to user for logging failures
        return False
    
    finally:
        if conn:
            conn.close()


def get_user_activity_log(user_id: int, limit: int = 100) -> List[Dict]:
    """Get recent activity log for a user."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT log_id, action, details, ip_address, timestamp
            FROM activity_log
            WHERE user_id = %s
            ORDER BY timestamp DESC
            LIMIT %s
        """
        cursor.execute(query, (user_id, limit))
        logs = cursor.fetchall()
        cursor.close()
        
        return logs
        
    except Error as e:
        st.error(f"❌ Error fetching activity log: {e}")
        return []
    
    finally:
        if conn:
            conn.close()


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def test_connection() -> bool:
    """Test database connection."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        st.error(f"❌ Database connection test failed: {e}")
        return False


if __name__ == "__main__":
    # Module test
    print("Miolingo Database Module v1.3.0")
    print("This module should be imported, not run directly.")
