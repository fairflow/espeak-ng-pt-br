# Miolingo Security Hardening Guide

**Date:** 13 November 2025  
**Branch:** feature/multi-user-auth-v1.3.0  
**Hosting:** Krystal Emerald Plan (£19/month) - Unlimited resources  
**Status:** 🛡️ **PRODUCTION-READY SECURITY ARCHITECTURE**

## 🎯 Overview

This document outlines comprehensive security hardening measures for Miolingo v1.3.0, leveraging the enhanced resources of the Krystal Emerald plan to implement industry-leading security practices.

---

## 🏗️ Infrastructure Security (Krystal Emerald)

### Hosting Advantages
- ✅ **Unlimited storage** - No database size constraints
- ✅ **Enhanced resources** - Higher concurrency, more CPU/RAM
- ✅ **Daily backups** - Automatic database snapshots
- ✅ **UK-based support** - Responsive security incident handling
- ✅ **Free SSL/TLS certificates** - Encrypted connections
- ✅ **DDoS protection** - Infrastructure-level mitigation

### Database Configuration
```python
# Optimized for Emerald plan resources
_connection_pool = pooling.MySQLConnectionPool(
    pool_name="miolingo_pool",
    pool_size=10,              # Increased from 5 (Emerald can handle more)
    pool_reset_session=True,   # Reset session state between uses
    autocommit=False,          # Explicit transaction control
    ssl_disabled=False,        # Enforce SSL/TLS encryption
    connection_timeout=10,     # Timeout for hung connections
    max_overflow=5,            # Extra connections during spikes
)
```

### MySQL Server Hardening (via cPanel)
1. **Set max_connections=100** (prevent resource exhaustion)
2. **Enable query logging** (forensics and debugging)
3. **Restrict remote access** (only specific IPs if possible)
4. **Use dedicated user** (not root, minimal privileges)
5. **Regular security updates** (automatic via Krystal managed hosting)

---

## 🔐 Authentication & Password Security

### Argon2id Parameters (Hardened for Emerald)
```python
from argon2 import PasswordHasher

# Aggressive parameters leveraging Emerald plan resources
pwd_hasher = PasswordHasher(
    time_cost=4,        # 4 iterations (increased from standard 3)
    memory_cost=102400, # 100 MB memory (increased from 64 MB)
    parallelism=8,      # 8 threads (increased from 4)
    hash_len=32,        # 32-byte hash output
    salt_len=16         # 16-byte random salt per password
)
```

**Why this is secure:**
- **Memory-hard:** Requires 100 MB RAM per hash = expensive for attackers
- **Time-cost:** 4 iterations = slower but more secure
- **Parallelism:** Uses 8 cores = can't be parallelized by attacker
- **Salt:** Unique per password = prevents rainbow table attacks
- **Emerald plan:** Has resources to handle these aggressive parameters without UX impact

### Password Requirements
```python
def validate_password(password: str) -> Tuple[bool, str]:
    """
    Enforce strong password requirements.
    """
    if len(password) < 10:
        return False, "Password must be at least 10 characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain lowercase letter"
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain digit"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain special character"
    
    # Check against common passwords (maintain a blacklist)
    common_passwords = ['Password123!', 'Admin123!', 'Qwerty123!']
    if password in common_passwords:
        return False, "Password too common, choose something unique"
    
    return True, "Password meets requirements"
```

### Session Security
```python
def create_session(user_id: int, ip_address: str) -> Optional[str]:
    """
    Create secure session with enhanced security.
    """
    # 32-byte cryptographically secure token (256 bits of entropy)
    session_id = secrets.token_urlsafe(32)
    
    # 24-hour expiration (force daily re-authentication)
    expires_at = datetime.now() + timedelta(hours=24)
    
    # Store session with IP validation
    query = """
        INSERT INTO sessions (session_id, user_id, created_at, expires_at, ip_address, user_agent)
        VALUES (%s, %s, NOW(), %s, %s, %s)
    """
    # user_agent can be captured from request headers
    
    return session_id


def validate_session(session_id: str, ip_address: str) -> Optional[Dict]:
    """
    Validate session with IP address check (detect hijacking).
    """
    query = """
        SELECT s.session_id, s.user_id, s.ip_address, u.username, u.email
        FROM sessions s
        JOIN users u ON s.user_id = u.user_id
        WHERE s.session_id = %s 
          AND s.expires_at > NOW()
          AND u.is_active = TRUE
    """
    
    result = execute_query(query, (session_id,))
    
    if result and result[0]['ip_address'] != ip_address:
        # IP address changed - potential session hijacking
        log_security_event(
            user_id=result[0]['user_id'],
            event="SESSION_IP_MISMATCH",
            details=f"Expected {result[0]['ip_address']}, got {ip_address}"
        )
        return None  # Invalidate session
    
    return result[0] if result else None
```

---

## 🚫 Rate Limiting & Anti-Abuse

### Rate Limit Implementation
```python
def check_rate_limit(
    identifier: str, 
    action: str, 
    max_attempts: int, 
    window_minutes: int
) -> bool:
    """
    Check if action is rate-limited. Returns True if allowed, False if blocked.
    
    Emerald plan allows more aggressive monitoring with unlimited storage.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
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
            # Log blocked attempt
            log_security_event(
                user_id=None,
                event="RATE_LIMIT_EXCEEDED",
                details=f"Action: {action}, Identifier: {identifier}"
            )
            return False
        
        # Log this attempt
        insert_query = """
            INSERT INTO rate_limits (identifier, action, attempt_time)
            VALUES (%s, %s, NOW())
        """
        cursor.execute(insert_query, (identifier, action))
        conn.commit()
        
        return True
    finally:
        cursor.close()
        conn.close()
```

### Rate Limit Rules (Enhanced for Production)
```python
RATE_LIMITS = {
    # Authentication
    'LOGIN_ATTEMPT': {'max': 5, 'window': 15},      # 5 per 15 min per username
    'REGISTRATION': {'max': 3, 'window': 60},       # 3 per hour per IP
    'PASSWORD_RESET': {'max': 3, 'window': 60},     # 3 per hour per email
    
    # Practice (increased capacity for Emerald)
    'PRACTICE_SUBMIT': {'max': 200, 'window': 60},  # 200 per hour per user
    'AUDIO_GENERATION': {'max': 300, 'window': 60}, # 300 per hour per user
    'AUDIO_RECORDING': {'max': 500, 'window': 60},  # 500 per hour per user
    
    # API (increased capacity for Emerald)
    'API_CALL': {'max': 500, 'window': 60},         # 500 per hour per user
    'SETTINGS_UPDATE': {'max': 100, 'window': 60},  # 100 per hour per user
}


def enforce_rate_limit(action: str, identifier: str = None):
    """
    Decorator for rate limiting Streamlit functions.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Use session user_id or IP address as identifier
            if identifier is None:
                ident = st.session_state.get('user_id', get_client_ip())
            else:
                ident = identifier
            
            limits = RATE_LIMITS.get(action)
            if limits and not check_rate_limit(
                ident, action, limits['max'], limits['window']
            ):
                st.error(f"⚠️ Too many attempts. Please try again later.")
                st.stop()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

### Failed Login Protection
```python
def handle_failed_login(username: str, ip_address: str):
    """
    Track failed login attempts and enforce lockout.
    """
    # Check failed attempts in last hour
    query = """
        SELECT COUNT(*) as failed_count
        FROM activity_log
        WHERE action = 'LOGIN_FAILED'
          AND details LIKE %s
          AND timestamp > DATE_SUB(NOW(), INTERVAL 1 HOUR)
    """
    result = execute_query(query, (f"%{username}%",))
    
    failed_count = result[0]['failed_count'] if result else 0
    
    if failed_count >= 10:
        # Lock account for 1 hour
        lock_query = """
            UPDATE users 
            SET is_active = FALSE, 
                lockout_until = DATE_ADD(NOW(), INTERVAL 1 HOUR)
            WHERE username = %s
        """
        execute_query(lock_query, (username,))
        
        # Send admin alert
        send_admin_alert(
            subject="Account Lockout",
            message=f"User {username} locked due to 10 failed login attempts from IP {ip_address}"
        )
        
        return False
    
    # Log failed attempt
    log_activity(
        user_id=None,
        action="LOGIN_FAILED",
        details=f"Username: {username}, IP: {ip_address}",
        ip_address=ip_address
    )
    
    return True
```

---

## 🛡️ Input Validation & Sanitization

### Username Validation
```python
def validate_username(username: str) -> Tuple[bool, str]:
    """
    Validate username format (prevent injection attacks).
    """
    if len(username) < 3 or len(username) > 20:
        return False, "Username must be 3-20 characters"
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Username can only contain letters, numbers, underscore, hyphen"
    
    # Check for reserved usernames
    reserved = ['admin', 'root', 'system', 'miolingo', 'support', 'moderator']
    if username.lower() in reserved:
        return False, "Username not available"
    
    return True, "Valid"
```

### Email Validation
```python
import re

def validate_email(email: str) -> Tuple[bool, str]:
    """
    RFC 5322 compliant email validation.
    """
    # Basic RFC 5322 regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    # Check email length
    if len(email) > 254:
        return False, "Email too long"
    
    # Optional: Check against disposable email services
    disposable_domains = ['tempmail.com', '10minutemail.com', 'guerrillamail.com']
    domain = email.split('@')[1]
    if domain in disposable_domains:
        return False, "Disposable email addresses not allowed"
    
    return True, "Valid"
```

### Practice Data Sanitization
```python
def sanitize_phrase(phrase: str) -> str:
    """
    Sanitize user-submitted phrase text.
    """
    # Remove HTML tags (prevent XSS)
    phrase = re.sub(r'<[^>]+>', '', phrase)
    
    # Remove script tags
    phrase = re.sub(r'<script.*?</script>', '', phrase, flags=re.DOTALL)
    
    # Limit length (prevent database bloat)
    phrase = phrase[:500]
    
    # Strip whitespace
    phrase = phrase.strip()
    
    return phrase


def validate_language_code(language_code: str) -> bool:
    """
    Whitelist validation for language codes.
    """
    SUPPORTED_LANGUAGES = ['pt-BR', 'fr-FR', 'nl-NL', 'nl-BE']
    return language_code in SUPPORTED_LANGUAGES
```

---

## 📊 Audit Logging & Monitoring

### Activity Logging
```python
def log_activity(
    user_id: Optional[int],
    action: str,
    details: str,
    ip_address: str
):
    """
    Log user activity for audit trail.
    Emerald plan unlimited storage allows comprehensive logging.
    """
    query = """
        INSERT INTO activity_log (user_id, action, details, ip_address, timestamp)
        VALUES (%s, %s, %s, %s, NOW())
    """
    execute_query(query, (user_id, action, details, ip_address))


# Log retention: 90 days (Emerald has unlimited storage)
def cleanup_old_logs():
    """
    Archive logs older than 90 days (for GDPR compliance).
    """
    query = """
        DELETE FROM activity_log
        WHERE timestamp < DATE_SUB(NOW(), INTERVAL 90 DAY)
    """
    execute_query(query, ())
```

### Security Event Monitoring
```python
def log_security_event(
    user_id: Optional[int],
    event: str,
    details: str,
    severity: str = 'MEDIUM'
):
    """
    Log security events for incident response.
    """
    log_activity(user_id, f"SECURITY_{event}", details, get_client_ip())
    
    # Send admin alert for HIGH severity
    if severity == 'HIGH':
        send_admin_alert(
            subject=f"Security Alert: {event}",
            message=f"User ID: {user_id}\nEvent: {event}\nDetails: {details}"
        )


# Security events to monitor:
SECURITY_EVENTS = [
    'SESSION_IP_MISMATCH',       # Potential session hijacking
    'RATE_LIMIT_EXCEEDED',       # Potential abuse
    'MULTIPLE_FAILED_LOGINS',    # Brute force attempt
    'SUSPICIOUS_REGISTRATION',   # Mass registration pattern
    'SQL_INJECTION_ATTEMPT',     # Detected malicious input
    'XSS_ATTEMPT',               # Cross-site scripting attempt
    'PRIVILEGE_ESCALATION',      # Unauthorized access attempt
]
```

### Anomaly Detection
```python
def detect_suspicious_activity(user_id: int) -> List[str]:
    """
    Detect suspicious patterns in user activity.
    """
    alerts = []
    
    # Check for multiple IPs in short time (account sharing or hijacking)
    query = """
        SELECT COUNT(DISTINCT ip_address) as ip_count
        FROM activity_log
        WHERE user_id = %s
          AND timestamp > DATE_SUB(NOW(), INTERVAL 1 HOUR)
    """
    result = execute_query(query, (user_id,))
    if result and result[0]['ip_count'] > 3:
        alerts.append("Multiple IP addresses detected")
    
    # Check for unusual practice volume (bot or abuse)
    query = """
        SELECT COUNT(*) as practice_count
        FROM user_progress
        WHERE user_id = %s
          AND practice_date > DATE_SUB(NOW(), INTERVAL 1 HOUR)
    """
    result = execute_query(query, (user_id,))
    if result and result[0]['practice_count'] > 100:
        alerts.append("Unusual practice volume detected")
    
    return alerts
```

---

## 🔒 Database Security

### SQL Injection Prevention
```python
# ✅ ALWAYS use parameterized queries
def get_user_by_username(username: str) -> Optional[Dict]:
    """
    Safe query using parameterized statements.
    """
    query = "SELECT * FROM users WHERE username = %s"
    result = execute_query(query, (username,))  # Tuple of parameters
    return result[0] if result else None


# ❌ NEVER concatenate user input into SQL
def unsafe_query(username: str):
    # THIS IS VULNERABLE TO SQL INJECTION - NEVER DO THIS!
    query = f"SELECT * FROM users WHERE username = '{username}'"
    # If username = "admin' OR '1'='1", entire table is returned!
```

### Database User Privileges
```sql
-- Create dedicated MySQL user (not root)
CREATE USER 'miolingo_app'@'%' IDENTIFIED BY 'strong_password';

-- Grant minimal required privileges
GRANT SELECT, INSERT, UPDATE, DELETE ON miolingo_users.* TO 'miolingo_app'@'%';

-- Revoke dangerous privileges
REVOKE DROP, CREATE, ALTER, INDEX ON *.* FROM 'miolingo_app'@'%';

FLUSH PRIVILEGES;
```

### Connection Security
```python
# Enforce SSL/TLS encryption
connection_config = {
    'host': st.secrets['mysql']['host'],
    'port': 3306,
    'database': st.secrets['mysql']['database'],
    'user': st.secrets['mysql']['user'],
    'password': st.secrets['mysql']['password'],
    'ssl_disabled': False,  # Enforce SSL/TLS
    'autocommit': False,    # Explicit transaction control
    'connection_timeout': 10,
}
```

---

## 🌐 DDoS & Network Security

### Connection Throttling
```python
def throttle_connections(ip_address: str) -> bool:
    """
    Limit concurrent connections per IP (prevent DDoS).
    """
    # Check active connections from this IP in last 10 seconds
    query = """
        SELECT COUNT(*) as conn_count
        FROM activity_log
        WHERE ip_address = %s
          AND action = 'CONNECTION_ATTEMPT'
          AND timestamp > DATE_SUB(NOW(), INTERVAL 10 SECOND)
    """
    result = execute_query(query, (ip_address,))
    
    if result and result[0]['conn_count'] > 10:
        log_security_event(
            user_id=None,
            event="CONNECTION_FLOOD",
            details=f"IP {ip_address} exceeded 10 connections in 10 seconds",
            severity='HIGH'
        )
        return False
    
    return True
```

### Cloudflare Integration (Optional)
```
If additional DDoS protection needed:
1. Point miolingo.io DNS to Cloudflare
2. Enable Cloudflare CDN + DDoS protection
3. Use Cloudflare's rate limiting rules
4. Benefit: Free tier includes basic DDoS protection
```

---

## 📋 GDPR Compliance & Data Privacy

### User Data Export
```python
def export_user_data(user_id: int) -> Dict:
    """
    Export all user data (GDPR right to data portability).
    """
    data = {
        'user_info': get_user_info(user_id),
        'settings': get_user_settings(user_id),
        'progress': get_all_user_progress(user_id),
        'activity_log': get_user_activity_log(user_id),
    }
    return data
```

### Account Deletion
```python
def delete_user_account(user_id: int):
    """
    Permanently delete user account and all associated data (GDPR right to erasure).
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Delete in order (respect foreign key constraints)
        cursor.execute("DELETE FROM sessions WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM user_settings WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM user_progress WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM activity_log WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        
        conn.commit()
        
        log_security_event(
            user_id=user_id,
            event="ACCOUNT_DELETED",
            details="User exercised GDPR right to erasure",
            severity='MEDIUM'
        )
    finally:
        cursor.close()
        conn.close()
```

### Data Minimization
```python
# Store ONLY essential PII
# ✅ Store: username, email, hashed password
# ❌ DON'T store: full name, address, phone, payment info, IP addresses long-term
```

---

## 🚀 Security Checklist (Pre-Production)

### Infrastructure
- [ ] MySQL user has minimal privileges (not root)
- [ ] Remote MySQL access restricted (if possible, specific IPs)
- [ ] SSL/TLS encryption enabled for database connections
- [ ] Connection pooling configured (max 10 connections)
- [ ] Daily backups enabled (verify via Krystal cPanel)
- [ ] Firewall rules configured (cPanel IP blocker)

### Authentication
- [ ] Argon2id password hashing with aggressive parameters
- [ ] Password requirements enforced (10+ chars, complexity)
- [ ] Session tokens are 32-byte cryptographically secure
- [ ] Session expiration set to 24 hours
- [ ] IP address validation on session use
- [ ] Failed login lockout after 10 attempts

### Rate Limiting
- [ ] Login attempts: 5 per 15 minutes
- [ ] Registration: 3 per hour per IP
- [ ] Practice submissions: 200 per hour per user
- [ ] API calls: 500 per hour per user
- [ ] Connection throttling: 10 per 10 seconds per IP

### Input Validation
- [ ] Username validation (3-20 chars, alphanumeric)
- [ ] Email validation (RFC 5322 compliant)
- [ ] Password validation (10+ chars, complexity)
- [ ] Language code whitelist validation
- [ ] Phrase sanitization (remove HTML/scripts, limit 500 chars)

### Logging & Monitoring
- [ ] Activity logging for all user actions
- [ ] Security event logging (session hijacking, rate limits)
- [ ] 90-day log retention policy
- [ ] Admin alerts for HIGH severity events
- [ ] Anomaly detection for suspicious patterns

### SQL Security
- [ ] All queries use parameterized statements
- [ ] No string concatenation with user input
- [ ] Database user has minimal privileges
- [ ] Connection timeout set to 10 seconds

### GDPR Compliance
- [ ] User data export function implemented
- [ ] Account deletion function implemented (cascade delete)
- [ ] Privacy policy and terms of service links added
- [ ] Data minimization practiced (only essential PII)

### Testing
- [ ] Penetration testing completed
- [ ] SQL injection testing completed
- [ ] XSS testing completed
- [ ] Rate limiting tested under load
- [ ] Session hijacking testing completed
- [ ] Load testing with 100+ concurrent users

---

## 🔧 Maintenance & Incident Response

### Weekly Tasks
- Review activity logs for suspicious patterns
- Check rate limit violations
- Verify backup completion
- Update Python dependencies for security patches

### Monthly Tasks
- Review and update password blacklist
- Analyze user growth patterns
- Check database performance metrics
- Review and update rate limit rules

### Incident Response Plan
1. **Detect** - Monitor logs, alerts, user reports
2. **Contain** - Block malicious IPs, lock compromised accounts
3. **Investigate** - Analyze logs, identify attack vector
4. **Remediate** - Patch vulnerabilities, reset credentials
5. **Document** - Log incident details, update security measures
6. **Notify** - Inform affected users (if data breach)

### Emergency Contacts
- Krystal Support: https://krystal.io/support
- Database Admin: [Your email]
- Security Lead: [Your email]

---

## 📚 References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [GDPR Compliance Guide](https://gdpr.eu/)
- [Argon2 RFC](https://datatracker.ietf.org/doc/html/rfc9106)
- [MySQL Security Best Practices](https://dev.mysql.com/doc/refman/8.0/en/security-guidelines.html)

---

## ✅ Next Steps

1. **Review this document** with your security requirements
2. **Implement security measures** in app_mysql.py
3. **Test thoroughly** (penetration testing, load testing)
4. **Deploy to production** with confidence
5. **Monitor continuously** for security events

**Emerald plan gives you the resources to implement enterprise-grade security without compromising UX!** 🛡️
