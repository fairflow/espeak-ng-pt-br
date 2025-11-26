#!/usr/bin/env python3
"""
Email Monitor for Miolingo Admin Dashboard
Read-only IMAP polling for io@miolingo.io

Credentials should be in .streamlit/secrets.toml:
[email]
imap_server = "mail.example.com"
imap_port = 993
email_address = "io@miolingo.io"
email_password = "your_password"
"""

import imaplib
import email
from email.header import decode_header
from datetime import datetime
from typing import List, Dict, Optional
import streamlit as st


class EmailMonitor:
    """Read-only IMAP email monitor."""
    
    def __init__(self):
        """Initialize with credentials from secrets."""
        try:
            self.imap_server = st.secrets["email"]["imap_server"]
            self.imap_port = st.secrets["email"]["imap_port"]
            self.email_address = st.secrets["email"]["email_address"]
            self.email_password = st.secrets["email"]["email_password"]
        except KeyError as e:
            raise ValueError(f"Missing email configuration in secrets.toml: {e}")
    
    def connect(self) -> imaplib.IMAP4_SSL:
        """Establish read-only IMAP connection."""
        try:
            # Connect to IMAP server with SSL
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            
            # Login
            mail.login(self.email_address, self.email_password)
            
            # Select INBOX in read-only mode (important!)
            mail.select('INBOX', readonly=True)
            
            return mail
        except imaplib.IMAP4.error as e:
            raise ConnectionError(f"IMAP connection failed: {e}")
        except Exception as e:
            raise ConnectionError(f"Connection error: {e}")
    
    def decode_header_value(self, value: str) -> str:
        """Decode email header value handling different encodings."""
        if not value:
            return ""
        
        decoded_parts = decode_header(value)
        result = []
        
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                try:
                    result.append(part.decode(encoding or 'utf-8'))
                except:
                    result.append(part.decode('utf-8', errors='ignore'))
            else:
                result.append(part)
        
        return ''.join(result)
    
    def fetch_recent_emails(self, limit: int = 20) -> List[Dict]:
        """
        Fetch recent emails from INBOX.
        
        Args:
            limit: Maximum number of emails to fetch
            
        Returns:
            List of email dictionaries with keys: id, from, subject, date, preview
        """
        emails = []
        mail = None
        
        try:
            mail = self.connect()
            
            # Search for all emails (most recent first)
            status, messages = mail.search(None, 'ALL')
            
            if status != 'OK':
                return []
            
            # Get list of email IDs
            email_ids = messages[0].split()
            
            # Get most recent emails (reverse order)
            recent_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            recent_ids = reversed(recent_ids)  # Most recent first
            
            for email_id in recent_ids:
                try:
                    # Fetch email
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    
                    if status != 'OK':
                        continue
                    
                    # Parse email
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    
                    # Extract headers
                    subject = self.decode_header_value(msg.get('Subject', '(No Subject)'))
                    from_addr = self.decode_header_value(msg.get('From', ''))
                    date_str = msg.get('Date', '')
                    
                    # Parse date
                    try:
                        date_tuple = email.utils.parsedate_tz(date_str)
                        if date_tuple:
                            timestamp = email.utils.mktime_tz(date_tuple)
                            date_obj = datetime.fromtimestamp(timestamp)
                        else:
                            date_obj = datetime.now()
                    except:
                        date_obj = datetime.now()
                    
                    # Extract body preview
                    body_preview = self.extract_body_preview(msg)
                    
                    emails.append({
                        'id': email_id.decode(),
                        'from': from_addr,
                        'subject': subject,
                        'date': date_obj,
                        'preview': body_preview
                    })
                    
                except Exception as e:
                    # Skip problematic emails
                    print(f"Error parsing email {email_id}: {e}")
                    continue
            
            return emails
            
        except Exception as e:
            raise Exception(f"Error fetching emails: {e}")
        
        finally:
            if mail:
                try:
                    mail.close()
                    mail.logout()
                except:
                    pass
    
    def extract_body_preview(self, msg: email.message.Message, max_length: int = 200) -> str:
        """Extract plain text preview from email body."""
        body = ""
        
        try:
            if msg.is_multipart():
                # Search for text/plain part
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == 'text/plain':
                        try:
                            payload = part.get_payload(decode=True)
                            charset = part.get_content_charset() or 'utf-8'
                            body = payload.decode(charset, errors='ignore')
                            break
                        except:
                            continue
            else:
                # Simple message
                try:
                    payload = msg.get_payload(decode=True)
                    charset = msg.get_content_charset() or 'utf-8'
                    body = payload.decode(charset, errors='ignore')
                except:
                    body = str(msg.get_payload())
        except:
            body = "(Could not extract body)"
        
        # Clean up and truncate
        body = body.strip()
        lines = body.split('\n')
        # Get first few non-empty lines
        preview_lines = [line.strip() for line in lines if line.strip()][:3]
        preview = ' '.join(preview_lines)
        
        if len(preview) > max_length:
            preview = preview[:max_length] + '...'
        
        return preview or "(Empty message)"
    
    def get_unread_count(self) -> int:
        """Get count of unread emails."""
        mail = None
        try:
            mail = self.connect()
            status, messages = mail.search(None, 'UNSEEN')
            
            if status == 'OK':
                email_ids = messages[0].split()
                return len(email_ids)
            
            return 0
        
        except Exception as e:
            print(f"Error getting unread count: {e}")
            return 0
        
        finally:
            if mail:
                try:
                    mail.close()
                    mail.logout()
                except:
                    pass
    
    def test_connection(self) -> tuple[bool, str]:
        """
        Test IMAP connection.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            mail = self.connect()
            mail.close()
            mail.logout()
            return (True, f"✅ Connected successfully to {self.email_address}")
        except Exception as e:
            return (False, f"❌ Connection failed: {e}")
