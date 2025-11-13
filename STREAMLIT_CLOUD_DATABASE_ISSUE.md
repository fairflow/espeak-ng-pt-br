# ⚠️ CRITICAL: Streamlit Community Cloud Database Limitation

**Date:** 13 November 2025  
**Branch:** feature/multi-user-auth-v1.3.0  
**Status:** 🔴 **BLOCKING ISSUE IDENTIFIED**

## 🚨 Problem

**Streamlit Community Cloud does NOT support persistent file storage.**

### Key Facts:
1. **Ephemeral File System:** All file writes are temporary and lost on app restart/reboot
2. **No SQLite Persistence:** Any SQLite database created will be wiped on reboot
3. **Session State Only:** `st.session_state` persists only for the duration of a single browser session
4. **No Built-in Database:** Streamlit Community Cloud does not provide a managed database service

### What This Means:
- ❌ Cannot use local SQLite (`users.db`) on Streamlit Cloud
- ❌ Cannot write to `practice_config.json` or `practice_history.json` persistently
- ❌ User accounts would be lost on every app restart
- ❌ Practice history would be lost on every app restart

## 🔍 Verification

From Streamlit documentation:
> "Session State exists for as long as the tab is open and connected to the Streamlit server. As soon as you close the tab, everything stored in Session State is lost."
> 
> "Session State is not persisted. If the Streamlit server crashes, then everything stored in Session State gets wiped."

Community Cloud runs on **ephemeral containers** - the file system is reset on:
- App restarts (manual or automatic)
- Code changes (auto-redeploy)
- Server maintenance
- Container recycling (can happen anytime)

## ✅ Solutions

### Option 1: External Database Service (RECOMMENDED)
Use a cloud database service for persistent storage:

**Free Tier Options:**
- ✅ **Supabase** (PostgreSQL-based, 500MB free, perfect for Streamlit)
- ✅ **PlanetScale** (MySQL, 5GB free, serverless)
- ✅ **Neon** (PostgreSQL, serverless, free tier)
- ✅ **Railway** (PostgreSQL, free tier with limits)
- ✅ **MongoDB Atlas** (NoSQL, 512MB free)

**Best Choice: Supabase**
- Built-in authentication (can replace our `app_auth.py`)
- Built-in user management
- Row-level security
- Real-time subscriptions
- REST API + Python client
- **Free tier: 500MB database, 50MB file storage**

### Option 2: Streamlit + Supabase Architecture

```
Streamlit Cloud (Frontend)
    ↓ (API calls via supabase-py)
Supabase (Backend)
    ├── PostgreSQL Database (user data, progress, settings)
    ├── Authentication (built-in)
    ├── Storage (for user uploads, optional)
    └── Row-Level Security (automatic data isolation)
```

**Benefits:**
- ✅ Zero infrastructure management
- ✅ Persistent data across app restarts
- ✅ Built-in auth (email/password, OAuth)
- ✅ Automatic backups
- ✅ Scales with user growth
- ✅ Free tier sufficient for MVP
- ✅ Easy migration to paid tier if needed

### Option 3: Keep Local Files for Development Only
- Use SQLite locally for development/testing
- Deploy to Streamlit Cloud with Supabase backend
- Environment detection: `if os.getenv("STREAMLIT_CLOUD"): use_supabase() else: use_sqlite()`

## 📋 Revised Implementation Plan

### Phase 1: Supabase Setup (2-3 days)
1. Create Supabase project (free tier)
2. Design database schema in Supabase
3. Set up authentication
4. Configure row-level security policies

### Phase 2: Supabase Integration (3-4 days)
1. Install `supabase-py` client
2. Create `app_supabase.py` module (replaces `app_database.py`)
3. Implement user authentication (use Supabase Auth)
4. Implement user settings storage
5. Implement progress tracking

### Phase 3: Local Development Mode (2 days)
1. Keep `app_database.py` for local SQLite
2. Add environment detection
3. Switch backend based on environment
4. Test both modes

### Phase 4: Testing & Deployment (3 days)
1. Test locally with SQLite
2. Test on Streamlit Cloud with Supabase
3. Migration script for any existing local data
4. Deploy to production

**Total Time: ~2 weeks**

## 🔧 Updated Architecture

### Development (Local)
```
app.py
├── app_auth.py (basic auth logic)
├── app_database.py (SQLite for local dev)
└── user_data/
    └── users.db (local only, git-ignored)
```

### Production (Streamlit Cloud)
```
Streamlit Cloud App
├── app.py (main UI)
├── app_auth.py (auth logic, uses Supabase)
└── app_supabase.py (Supabase client & API)
    ↓
Supabase Cloud
├── PostgreSQL Database
│   ├── users table
│   ├── user_settings table
│   ├── user_progress table
│   └── sessions table
└── Authentication Service
```

## 💰 Cost Analysis

### Supabase Free Tier:
- ✅ **500MB database** (plenty for MVP, ~5000-10000 users)
- ✅ **50MB file storage** (for user uploads if needed)
- ✅ **2GB bandwidth/month** (sufficient for text-based app)
- ✅ **50,000 monthly active users** (way more than we need initially)
- ✅ **Unlimited API requests**
- ✅ **Social OAuth** included (Google, GitHub, etc.)

### When to Upgrade:
- **$25/month** (Pro) when you exceed:
  - 8GB database size
  - 100GB bandwidth
  - Need dedicated resources

### Comparison to Alternatives:
- **Heroku Postgres:** $5/month minimum (10K rows limit)
- **AWS RDS:** $15/month minimum
- **Google Cloud SQL:** $10/month minimum
- **Supabase:** $0/month (free forever for small apps)

## 🚀 Action Items

### Immediate (This Week):
1. ✅ **Create feature branch** (done: `feature/multi-user-auth-v1.3.0`)
2. ✅ **Remove CAPTCHA from plan** (per user request)
3. ⏳ **Sign up for Supabase** (free account)
4. ⏳ **Create Supabase project** for Miolingo
5. ⏳ **Design database schema** in Supabase
6. ⏳ **Update implementation plan** with Supabase integration

### Next Week:
1. Implement Supabase client module
2. Integrate authentication with Supabase Auth
3. Test locally with SQLite fallback
4. Deploy MVP to Streamlit Cloud with Supabase

## 📚 Resources

### Supabase Documentation:
- Getting Started: https://supabase.com/docs
- Python Client: https://supabase.com/docs/reference/python/introduction
- Authentication: https://supabase.com/docs/guides/auth
- Row-Level Security: https://supabase.com/docs/guides/auth/row-level-security
- Streamlit Integration Examples: https://supabase.com/docs/guides/getting-started/tutorials/with-streamlit

### Example Code:
```python
# app_supabase.py
from supabase import create_client, Client
import streamlit as st

@st.cache_resource
def get_supabase_client() -> Client:
    """Initialize Supabase client (cached)"""
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

def register_user(email: str, password: str) -> dict:
    """Register new user via Supabase Auth"""
    supabase = get_supabase_client()
    return supabase.auth.sign_up({
        "email": email,
        "password": password
    })

def login_user(email: str, password: str) -> dict:
    """Login user via Supabase Auth"""
    supabase = get_supabase_client()
    return supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })

def save_user_setting(user_id: str, key: str, value: any) -> None:
    """Save user setting to Supabase"""
    supabase = get_supabase_client()
    supabase.table("user_settings").upsert({
        "user_id": user_id,
        "setting_key": key,
        "setting_value": value
    }).execute()

def save_practice(user_id: str, language: str, practice_data: dict) -> None:
    """Save practice record to Supabase"""
    supabase = get_supabase_client()
    supabase.table("user_progress").insert({
        "user_id": user_id,
        "language_code": language,
        "practice_date": practice_data["date"],
        "target_phrase": practice_data["target"],
        "recognized_phrase": practice_data["recognized"],
        "similarity_score": practice_data["similarity"],
        "perfect_match": practice_data["match"]
    }).execute()
```

## ❓ Decision Required

**Do you want to:**

1. ✅ **Proceed with Supabase** (recommended)
   - Free tier sufficient for MVP
   - Built-in auth simplifies implementation
   - Production-ready from day 1
   - Scalable as app grows

2. ⏸️ **Wait and research alternatives**
   - Explore other database options
   - Consider self-hosted solutions
   - Delay multi-user feature

3. 🔄 **Pivot to different architecture**
   - Use Streamlit secrets for static user list (very limited)
   - Consider Snowflake (if you have access)
   - Build separate FastAPI backend

**My recommendation: Option 1 (Supabase)**
- Fastest path to production
- Zero cost for MVP
- Battle-tested with Streamlit apps
- Reduces implementation complexity

---

## 🎯 Next Steps After Decision

**If Supabase approved:**
1. I'll create Supabase setup guide
2. Update `MULTI_USER_IMPLEMENTATION_PLAN.md`
3. Start implementation with Supabase integration
4. Keep local SQLite for development/testing

**What do you think?** 🤔
