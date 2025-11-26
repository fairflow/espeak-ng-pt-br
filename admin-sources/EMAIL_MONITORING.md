# Email Monitoring Feature

Read-only IMAP email monitoring for Miolingo admin dashboard.

## Features

- ✅ **Read-only mode**: No modifications possible to email account
- 📬 View recent emails (up to 30 most recent)
- 📊 Unread email count
- 🔍 Email preview with from/subject/date/body preview
- 🔌 Connection test
- 🔄 Manual refresh

## Setup

1. **Add credentials to `.streamlit/secrets.toml`:**

```toml
[email]
imap_server = "mail.yourdomain.com"
imap_port = 993
email_address = "io@miolingo.io"
email_password = "your_password"
```

See `email_secrets_template.toml` for examples with different providers.

2. **Restart admin dashboard:**

```bash
streamlit run miolingo-admin.py --server.port 8505
```

3. **Access Email tab** in the admin dashboard

## Files

- `email_monitor.py` - Core IMAP monitoring class
- `email_secrets_template.toml` - Configuration template
- `miolingo-admin.py` - Admin dashboard with Email tab

## Security

- **Read-only**: All IMAP connections use `readonly=True` mode
- **No modifications**: Cannot delete, move, or mark emails as read
- **Local only**: Email credentials only in local `.streamlit/secrets.toml`
- **Not committed**: secrets.toml is in .gitignore

## Usage

The Email tab will:
- Show up to 30 most recent emails
- Display unread count
- Allow testing IMAP connection
- Show email preview (first few lines of body)
- Display full headers (from, date, subject)

No emails can be modified, deleted, or marked as read from this interface.

## Troubleshooting

If connection fails:
1. Check IMAP server address and port
2. Verify email password is correct
3. For Gmail: Use App Password, not regular password
4. Check firewall allows port 993 (IMAP SSL)
5. Click "Test Connection" button to see specific error

## Future Enhancements (Optional)

- Auto-refresh at intervals
- Filter by sender/subject
- Mark emails as read (when needed)
- Reply to emails (when needed)
- Archive management
