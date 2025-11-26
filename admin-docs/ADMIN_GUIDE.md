# Miolingo Admin Dashboard Guide

**Version 1.7.0**

## Overview

The Miolingo Admin Dashboard is a local monitoring and management interface for the Miolingo pronunciation training application. It provides real-time insights into system resources, user activity, logs, email monitoring, and configuration.

## Access

- **URL**: http://localhost:8505
- **Start**: `streamlit run miolingo-admin.py --server.port 8505`
- **Requirements**: Local access only, database credentials in `.streamlit/secrets.toml`

## Features

### 1. Resource Usage

Monitor system resource consumption:
- Google Cloud TTS usage and quota
- Whisper model status and downloads
- Audio processing activity
- Database connection status

### 2. Current Users

View and manage users:
- Total user count
- Currently logged-in users with session details
- Expired sessions
- Recent user signups
- User activity statistics (30-day chart)
- Selective force logout
- Clean up expired sessions

### 3. Logs

Access application logs:
- Local practice history
- Database activity logs
- Session information

### 4. Email Monitor

Read-only email monitoring for io@miolingo.io:
- View recent emails (up to 30)
- Unread count
- Email preview with from/subject/date
- Connection test
- Manual refresh

**Security**: All email operations are read-only. No emails can be modified or deleted.

### 5. Settings & Configuration

System configuration:
- Secrets status (Google Cloud TTS, MySQL, SSH)
- Installed packages check
- Quick actions (clear cache, reload)

## Quick Actions

**Sidebar Button**: "🔄 Clear Cache & Reconnect"
- Use when seeing connection errors
- Clears cached connections and data
- Forces fresh database reconnection

## Connection Issues

The SSH tunnel to the database may timeout after inactivity. If you see "MySQL Connection not available":

1. Click sidebar "🔄 Clear Cache & Reconnect"
2. Click "Retry Connection" in error message
3. Refresh browser tab

The connection cache auto-refreshes every 5 minutes.

## Configuration

Required in `.streamlit/secrets.toml`:

```toml
[mysql]
host = "localhost"
port = 3306
user = "your_user"
password = "your_password"
database = "your_database"

[ssh]
host = "your_ssh_host"
port = 22
username = "your_ssh_user"
password = "your_ssh_password"

[email]
imap_server = "mail.yourdomain.com"
imap_port = 993
email_address = "io@miolingo.io"
email_password = "your_password"
```

## Version Management

Use `bump_admin.py` to manage admin dashboard versions:

```bash
source venv/bin/activate
bump_admin.py patch          # Bump version
bump_admin.py minor tag      # Bump + commit + tag
bump_admin.py patch tag push # Bump + commit + tag + push
```

Admin versions are tagged separately as `admin-v1.6.0`.

## Files

- `miolingo-admin.py` - Main dashboard application
- `email_monitor.py` - Email monitoring module
- `check_sessions.py` - Database session checker utility
- `admin-docs/` - Documentation
- `admin-sources/` - Additional administrative files

## Security

- **Local only**: Dashboard runs on localhost:8505
- **No external access**: Not deployed to cloud
- **Read-only email**: Email monitoring cannot modify messages
- **Database access**: Uses same secure SSH tunnel as main app

## Troubleshooting

### Dashboard won't start
- Check if port 8505 is already in use: `lsof -i:8505`
- Kill existing process: `pkill -f "miolingo-admin.py"`

### Database connection fails
- Verify SSH tunnel is active
- Check MySQL credentials in secrets.toml
- Use "Clear Cache & Reconnect" button

### Email not working
- Verify email credentials in secrets.toml
- Test connection using "Test Connection" button
- Check IMAP port (usually 993 for SSL)
- For Gmail: Use App Password

## Support

For issues or questions:
- Check logs in the Logs tab
- Verify configuration in Settings tab
- Review EMAIL_MONITORING.md for email setup
