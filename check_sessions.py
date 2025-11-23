#!/usr/bin/env python3
"""
Quick script to check current database sessions and guest users.
"""

import app_mysql
from datetime import datetime

print("=" * 80)
print("DATABASE SESSION AND USER CHECK")
print("=" * 80)

# Get database connection
conn = None
try:
    conn = app_mysql.get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Check all users
    print("\n--- ALL USERS ---")
    cursor.execute("""
        SELECT user_id, username, email, created_at, is_active
        FROM users
        ORDER BY created_at DESC
        LIMIT 20
    """)
    users = cursor.fetchall()
    
    if users:
        print(f"\nTotal users found: {len(users)}")
        print(f"{'ID':<6} {'Username':<30} {'Email':<40} {'Created':<20} {'Active'}")
        print("-" * 120)
        for user in users:
            guest_marker = " 🎭" if user['username'].startswith('guest_') else ""
            print(f"{user['user_id']:<6} {user['username']:<30}{guest_marker} {user['email']:<40} {user['created_at']} {user['is_active']}")
    else:
        print("No users found")
    
    # Check active sessions
    print("\n--- ACTIVE SESSIONS ---")
    cursor.execute("""
        SELECT s.session_id, s.user_id, s.ip_address, s.created_at, s.expires_at,
               u.username, u.email
        FROM sessions s
        JOIN users u ON s.user_id = u.user_id
        WHERE s.expires_at > NOW()
        ORDER BY s.created_at DESC
    """)
    sessions = cursor.fetchall()
    
    if sessions:
        print(f"\nTotal active sessions: {len(sessions)}")
        print(f"{'User ID':<8} {'Username':<30} {'IP Address':<15} {'Created':<20} {'Expires'}")
        print("-" * 120)
        for session in sessions:
            guest_marker = " 🎭" if session['username'].startswith('guest_') else ""
            print(f"{session['user_id']:<8} {session['username']:<30}{guest_marker} {session['ip_address']:<15} {session['created_at']} {session['expires_at']}")
    else:
        print("No active sessions found")
    
    # Check guest users specifically
    print("\n--- GUEST USERS ---")
    cursor.execute("""
        SELECT user_id, username, email, created_at
        FROM users
        WHERE username LIKE 'guest_%'
        ORDER BY created_at DESC
    """)
    guests = cursor.fetchall()
    
    if guests:
        print(f"\nTotal guest users: {len(guests)}")
        print(f"{'ID':<6} {'Username':<40} {'Created'}")
        print("-" * 80)
        for guest in guests:
            print(f"{guest['user_id']:<6} {guest['username']:<40} {guest['created_at']}")
    else:
        print("No guest users found")
    
    # Check recent activity log
    print("\n--- RECENT ACTIVITY (last 10) ---")
    cursor.execute("""
        SELECT a.activity_id, a.user_id, u.username, a.action, a.details, a.timestamp
        FROM activity_log a
        JOIN users u ON a.user_id = u.user_id
        ORDER BY a.timestamp DESC
        LIMIT 10
    """)
    activities = cursor.fetchall()
    
    if activities:
        for activity in activities:
            guest_marker = " 🎭" if activity['username'].startswith('guest_') else ""
            print(f"\n[{activity['timestamp']}] {activity['username']}{guest_marker}")
            print(f"  Action: {activity['action']}")
            print(f"  Details: {activity['details']}")
    else:
        print("No recent activity")
    
    cursor.close()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    if conn and conn.is_connected():
        conn.close()

print("\n" + "=" * 80)
