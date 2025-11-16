#!/usr/bin/env python3
"""
Miolingo Admin Dashboard

Local admin interface for monitoring resource usage, users, and logs.
Run with: streamlit run miolingo-admin.py
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
from collections import defaultdict

# Page config
st.set_page_config(
    page_title="Miolingo Admin",
    page_icon="🔧",
    layout="wide"
)

st.title("🔧 Miolingo Admin Dashboard")
st.caption("Local monitoring and management interface")

# Database connection helper
@st.cache_resource
def get_db_connection():
    """Get database connection using app_mysql module."""
    try:
        # Import the app's MySQL module which handles SSH tunnel properly
        import sys
        from pathlib import Path
        
        # Add app directory to path if needed
        app_dir = Path(__file__).parent
        if str(app_dir) not in sys.path:
            sys.path.insert(0, str(app_dir))
        
        from app_mysql import get_connection
        
        # Test connection
        conn = get_connection()
        return conn, None  # No separate tunnel object needed
        
    except Exception as e:
        st.warning(f"Database connection error: {e}")
        return None, None

# Tab layout
tab1, tab2, tab3, tab4 = st.tabs(["📊 Resource Usage", "👥 Users", "📝 Logs", "⚙️ Settings"])

# TAB 1: Resource Usage
with tab1:
    st.header("📊 Resource Usage")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🗣️ TTS Usage")
        
        # Check for Google Cloud TTS quota
        try:
            # Check for API key at root level or in section
            has_gcloud = ("google_cloud_tts_api_key" in st.secrets) or ("google_cloud_tts" in st.secrets)
            
            if has_gcloud:
                st.success("✓ Google Cloud TTS configured")
                
                # Calculate actual usage from database
                conn, tunnel = get_db_connection()
                if conn:
                    try:
                        cursor = conn.cursor(dictionary=True)
                        
                        # Get count of practice sessions this month (each generates TTS)
                        cursor.execute("""
                            SELECT COUNT(*) as count,
                                   SUM(LENGTH(target_phrase)) as total_chars
                            FROM user_progress
                            WHERE practice_date >= DATE_FORMAT(NOW(), '%Y-%m-01')
                        """)
                        usage = cursor.fetchone()
                        
                        # Convert Decimal to int/float for Streamlit
                        session_count = int(usage['count'] or 0)
                        char_count = int(usage['total_chars'] or 0)
                        
                        # Show actual usage
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.metric("TTS Requests (This Month)", f"{session_count:,}")
                        with col_b:
                            st.metric("Characters Used", f"{char_count:,}")
                        
                        # Calculate percentage of free tier
                        free_tier_limit = 1_000_000
                        usage_pct = float(char_count) / float(free_tier_limit) * 100
                        
                        st.progress(min(usage_pct / 100.0, 1.0))
                        st.caption(f"**{usage_pct:.1f}%** of free tier used ({char_count:,} / {free_tier_limit:,} characters)")
                        
                        # Show quota information
                        st.info("""
                        **Google Cloud TTS Quotas:**
                        - Free tier: 1M characters/month
                        - Standard: ~4M characters/month
                        - Neural: ~1M characters/month
                        """)
                        
                        cursor.close()
                    except Exception as e:
                        st.warning(f"Could not fetch usage: {e}")
                        st.info("**Estimated capacity:** ~20,000 phrases/month (free tier)")
                else:
                    st.info("**Average phrase:** ~50 characters\n**Estimated capacity:** ~20,000 phrases/month (free tier)")
            else:
                st.warning("Google Cloud TTS not configured in secrets")
        except Exception as e:
            st.warning(f"Error checking TTS config: {e}")
        
        # Show gTTS status
        st.write("**gTTS (Free, unlimited):**")
        try:
            import gtts
            st.success("✓ gTTS available")
        except:
            st.error("✗ gTTS not installed")
    
    with col2:
        st.subheader("💾 Storage Usage")
        
        # Check language materials size
        materials_dir = Path("language_materials")
        if materials_dir.exists():
            total_size = sum(f.stat().st_size for f in materials_dir.rglob('*') if f.is_file())
            st.metric("Language Materials", f"{total_size / 1024 / 1024:.2f} MB")
            
            # Count files by language
            lang_counts = defaultdict(int)
            for lang_dir in materials_dir.iterdir():
                if lang_dir.is_dir():
                    count = sum(1 for f in lang_dir.rglob('*.txt'))
                    lang_counts[lang_dir.name] = count
            
            st.write("**Files by language:**")
            for lang, count in sorted(lang_counts.items()):
                st.text(f"  {lang}: {count} files")
        else:
            st.warning("Language materials directory not found")
    
    with col3:
        st.subheader("🔌 API Status")
        
        # Check Whisper model
        st.write("**Speech Recognition:**")
        try:
            import whisper
            st.success("✓ Whisper available")
            
            # Check for downloaded models
            model_dir = Path.home() / ".cache" / "whisper"
            if model_dir.exists():
                models = list(model_dir.glob("*.pt"))
                st.text(f"  Downloaded models: {len(models)}")
        except:
            st.warning("✗ Whisper not installed")
        
        # Check database
        st.write("**Database:**")
        conn, tunnel = get_db_connection()
        if conn:
            st.success("✓ Database connected")
            # Connection returned to pool automatically
        else:
            st.warning("✗ Database not connected")

# TAB 2: Users
with tab2:
    st.header("👥 Current Users")
    
    conn, tunnel = get_db_connection()
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Get user count
            cursor.execute("SELECT COUNT(*) as count FROM users")
            user_count = cursor.fetchone()['count']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Users", user_count)
            
            # Get currently logged-in users (active sessions)
            cursor.execute("""
                SELECT u.username, u.email, s.created_at as login_time, s.ip_address
                FROM sessions s
                JOIN users u ON s.user_id = u.user_id
                WHERE s.expires_at > NOW()
                ORDER BY s.created_at DESC
            """)
            active_sessions = cursor.fetchall()
            
            with col2:
                st.metric("Currently Logged In", len(active_sessions))
            
            # Show expired sessions count
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM sessions
                WHERE expires_at <= NOW()
            """)
            expired_count = int(cursor.fetchone()['count'] or 0)
            
            with col3:
                st.metric("Expired Sessions", expired_count, delta="⚠️" if expired_count > 0 else None)
            
            # Cleanup button for expired sessions
            if expired_count > 0:
                if st.button("🧹 Clean Up Expired Sessions", type="secondary"):
                    try:
                        from app_mysql import cleanup_expired_sessions
                        deleted = cleanup_expired_sessions()
                        st.success(f"✅ Removed {deleted} expired sessions")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Cleanup failed: {e}")
            
            if active_sessions:
                st.subheader("🟢 Currently Logged In Users")
                df_active = pd.DataFrame(active_sessions)
                df_active['login_time'] = pd.to_datetime(df_active['login_time'])
                st.dataframe(df_active, use_container_width=True, hide_index=True)
                st.caption("💡 Active sessions expire after 24 hours of inactivity. Sessions are removed on logout or expiration.")
            else:
                st.info("No users currently logged in")
            
            # Show expired sessions if any
            if expired_count > 0:
                with st.expander(f"⚠️ View {expired_count} Expired Sessions (not yet cleaned up)"):
                    cursor.execute("""
                        SELECT u.username, u.email, s.created_at as login_time, s.expires_at
                        FROM sessions s
                        JOIN users u ON s.user_id = u.user_id
                        WHERE s.expires_at <= NOW()
                        ORDER BY s.expires_at DESC
                    """)
                    expired_sessions = cursor.fetchall()
                    if expired_sessions:
                        df_expired = pd.DataFrame(expired_sessions)
                        df_expired['login_time'] = pd.to_datetime(df_expired['login_time'])
                        df_expired['expires_at'] = pd.to_datetime(df_expired['expires_at'])
                        st.dataframe(df_expired, use_container_width=True, hide_index=True)
            
            st.divider()
            
            # Get recent users
            cursor.execute("""
                SELECT username, email, created_at 
                FROM users 
                ORDER BY created_at DESC 
                LIMIT 20
            """)
            users = cursor.fetchall()
            
            if users:
                st.subheader("Recent Users")
                df = pd.DataFrame(users)
                df['created_at'] = pd.to_datetime(df['created_at'])
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No users found")
            
            # Get user activity stats
            try:
                cursor.execute("""
                    SELECT 
                        DATE(created_at) as date,
                        COUNT(*) as signups
                    FROM users
                    WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                    GROUP BY DATE(created_at)
                    ORDER BY date DESC
                """)
                activity = cursor.fetchall()
                
                if activity:
                    st.subheader("Signups (Last 30 Days)")
                    df_activity = pd.DataFrame(activity)
                    st.line_chart(df_activity.set_index('date'))
            except Exception as e:
                st.warning(f"Could not load activity stats: {e}")
            
            cursor.close()
            # Connection returned to pool automatically
                
        except Exception as e:
            st.error(f"Database error: {e}")
            # Connection returned to pool automatically
    else:
        st.warning("Database connection not available. User data not accessible.")

# TAB 3: Logs
with tab3:
    st.header("📝 Recent Logs")
    
    # Check for Streamlit Cloud logs
    st.info("For production logs, check Streamlit Cloud dashboard: https://share.streamlit.io/")
    
    # Local log viewer
    st.subheader("Local Application Events")
    
    # Look for practice history files (user activity indicator)
    history_file = Path("practice_history.json")
    if history_file.exists():
        try:
            with open(history_file, 'r') as f:
                history = json.load(f)
            
            if isinstance(history, list) and len(history) > 0:
                st.metric("Local Practice Sessions", len(history))
                
                # Show recent sessions
                st.write("**Recent Sessions:**")
                recent = history[-10:][::-1]  # Last 10, reversed
                
                for i, session in enumerate(recent, 1):
                    with st.expander(f"Session {i} - {session.get('timestamp', 'Unknown time')}"):
                        st.json(session)
            else:
                st.info("No practice history recorded")
        except Exception as e:
            st.warning(f"Could not read practice history: {e}")
    else:
        st.info("No local practice history file found")
    
    # Database activity logs
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Try to get recent sessions if table exists
            try:
                cursor.execute("""
                    SELECT * FROM practice_sessions 
                    ORDER BY created_at DESC 
                    LIMIT 20
                """)
                sessions = cursor.fetchall()
                
                if sessions:
                    st.subheader("Recent Practice Sessions (Database)")
                    df = pd.DataFrame(sessions)
                    st.dataframe(df, use_container_width=True, hide_index=True)
            except Exception as e:
                st.info("Practice sessions table not available")
            
            cursor.close()
        except Exception as e:
            st.warning(f"Could not fetch logs: {e}")

# TAB 4: Settings
with tab4:
    st.header("⚙️ Settings & Configuration")
    
    st.subheader("🔑 Secrets Status")
    
    # Check for secrets
    try:
        has_gcloud = ("google_cloud_tts_api_key" in st.secrets) or ("google_cloud_tts" in st.secrets)
        
        secrets_available = {
            "Google Cloud TTS": has_gcloud,
            "MySQL Database": "mysql" in st.secrets,
            "SSH Tunnel": "ssh" in st.secrets,
        }
        
        for service, available in secrets_available.items():
            if available:
                st.success(f"✓ {service} configured")
            else:
                st.warning(f"✗ {service} not configured")
    except:
        st.error("No secrets file found. Create `.streamlit/secrets.toml`")
    
    st.subheader("📦 Installed Packages")
    
    # Check key dependencies
    packages = {
        "streamlit": "Web framework",
        "whisper": "Speech recognition",
        "gtts": "Text-to-speech (free)",
        "mysql.connector": "Database",
        "sshtunnel": "SSH tunneling",
        "soundfile": "Audio processing",
        "numpy": "Numerical processing",
    }
    
    for package, description in packages.items():
        try:
            __import__(package.replace("-", "_"))
            st.success(f"✓ {package} - {description}")
        except ImportError:
            st.error(f"✗ {package} - {description} (not installed)")
    
    st.subheader("🔄 Quick Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear Cache"):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.success("Cache cleared!")
            st.rerun()
    
    with col2:
        if st.button("📊 Reload Data"):
            st.rerun()

# Footer
st.divider()
st.caption("Miolingo Admin Dashboard v1.5.0 | Local monitoring interface")
