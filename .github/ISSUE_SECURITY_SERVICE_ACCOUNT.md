# Security Enhancement: Migrate to Service Account Keys for Google Cloud TTS

## Priority: High
**Category:** Security, Best Practices  
**Created:** 2025-11-14

## Problem Statement
Currently using Google Cloud API keys for Text-to-Speech authentication, which violates several security best practices:

1. **API Keys in repositories:** While `.streamlit/secrets.toml` is gitignored, API keys are less secure than Service Account credentials
2. **Broad permissions:** API keys cannot be scoped to specific resources or operations
3. **Rotation challenges:** API keys are harder to rotate without service disruption
4. **No audit trail:** Limited ability to track which service/user made specific API calls
5. **Client-side exposure risk:** API keys more easily exposed in client applications

## Security Best Practices from Google Cloud Documentation

From Google's official guidance:
- ✅ **Restrict your API key** (partially implemented)
- ❌ **Delete unneeded API keys to minimise exposure to attacks**
- ❌ **Delete and recreate your API keys periodically**
- ✅ **Don't include API keys in client code or commit them to code repositories**
- ❌ **Implement strong monitoring and logging**

## Recommended Solution: Service Account Keys

### Benefits
1. **Fine-grained permissions:** IAM roles can be scoped to only Text-to-Speech API
2. **Better audit trail:** Cloud Audit Logs track all API calls with service account identity
3. **Easier rotation:** Multiple keys can exist simultaneously for zero-downtime rotation
4. **Workload Identity support:** Can migrate to more secure credential-free authentication later
5. **Industry standard:** Service accounts are the recommended authentication method for server-to-server communication

### Implementation Plan

#### Phase 1: Service Account Setup (Immediate)
1. Create dedicated service account: `miolingo-tts@PROJECT_ID.iam.gserviceaccount.com`
2. Grant minimal IAM role: `roles/cloudtts.user` (Text-to-Speech API User)
3. Generate JSON key file
4. Store JSON in Streamlit Cloud secrets (NOT in git)
5. Update `app.py` to use Service Account authentication:
   ```python
   from google.oauth2 import service_account
   import json
   
   credentials_json = st.secrets.get("google_cloud_tts_credentials")
   credentials = service_account.Credentials.from_service_account_info(
       json.loads(credentials_json)
   )
   client = texttospeech.TextToSpeechClient(credentials=credentials)
   ```

#### Phase 2: Monitoring & Logging (1-2 weeks)
1. Enable Cloud Audit Logs for Text-to-Speech API
2. Set up budget alerts in Google Cloud Console ($5/month threshold)
3. Create Streamlit dashboard for TTS usage monitoring
4. Implement error logging for failed TTS API calls

#### Phase 3: Key Rotation Policy (Ongoing)
1. Document key rotation procedure in `DEVELOPER_GUIDE.md`
2. Set calendar reminder for quarterly key rotation
3. Create automation script for key rotation (future enhancement)
4. Maintain 2 active keys during rotation period

#### Phase 4: Advanced Security (Future)
1. Investigate Workload Identity Federation for credential-free auth
2. Implement VPC Service Controls if scaling beyond hobby project
3. Add API rate limiting in application layer
4. Consider dedicated GCP project for production vs development

### Code Changes Required

**app.py modifications:**
```python
# Replace lines ~467-470 (current API key approach):
# OLD:
api_key = st.secrets.get("google_cloud_tts_api_key", None)
if not api_key:
    raise ValueError("google_cloud_tts_api_key not found in secrets")
client = texttospeech.TextToSpeechClient(client_options={"api_key": api_key})

# NEW:
credentials_json = st.secrets.get("google_cloud_tts_credentials", None)
if not credentials_json:
    raise ValueError("google_cloud_tts_credentials not found in secrets")

credentials = service_account.Credentials.from_service_account_info(
    json.loads(credentials_json)
)
client = texttospeech.TextToSpeechClient(credentials=credentials)
```

**Streamlit Cloud Secrets format:**
```toml
# Instead of:
# google_cloud_tts_api_key = "AIza..."

# Use entire JSON key content:
google_cloud_tts_credentials = '''
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "miolingo-tts@your-project-id.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
'''
```

### Testing Plan
1. Create new service account in Google Cloud Console
2. Test locally with service account credentials in `.streamlit/secrets.toml`
3. Verify audio generation works for all supported languages (pt-BR, pt-PT, fr-FR, nl-NL, nl-BE)
4. Deploy to Streamlit Cloud with new credentials
5. Monitor for any authentication errors over 24-hour period
6. Delete old API key after confirming service account works

### Documentation Updates Required
- `app-docs/DEVELOPER_GUIDE.md`: Add service account setup instructions
- `app-docs/DEPLOYMENT.md`: Update Streamlit Cloud secrets configuration
- `VERSION_WORKFLOW.md`: Add security credential rotation to release checklist
- `README.md`: Mention security best practices in "Contributing" section

### Risks & Mitigation
- **Risk:** Service account key compromised
  - **Mitigation:** Key is stored only in Streamlit Cloud secrets (encrypted at rest), not in git
  - **Mitigation:** Enable Cloud Audit Logs to detect unusual API usage patterns
  
- **Risk:** Downtime during migration from API key to service account
  - **Mitigation:** Test thoroughly in local environment first
  - **Mitigation:** Deploy during low-traffic period with maintenance banner
  - **Mitigation:** Keep old API key active until service account confirmed working

- **Risk:** Increased complexity for new contributors
  - **Mitigation:** Comprehensive documentation in DEVELOPER_GUIDE.md
  - **Mitigation:** Include troubleshooting section for common auth errors

### Success Metrics
- ✅ No API keys in codebase or documentation
- ✅ Service account has minimal required IAM permissions
- ✅ Cloud Audit Logs show all TTS API calls with service account identity
- ✅ Budget alerts configured and working
- ✅ Key rotation procedure documented and tested
- ✅ Zero authentication-related downtime during migration

## References
- [Google Cloud Service Accounts Best Practices](https://cloud.google.com/iam/docs/best-practices-service-accounts)
- [Google Cloud TTS Authentication](https://cloud.google.com/text-to-speech/docs/authentication)
- [API Key Best Practices](https://cloud.google.com/docs/authentication/api-keys)
- [Streamlit Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)

## Related Issues
- #5 Database-backed maintenance messaging system
- Future: Implement comprehensive security audit logging

---
**Current Status:** Using API key (working, but suboptimal)  
**Target Status:** Service account with monitoring and rotation policy  
**Estimated Effort:** 2-4 hours initial setup + documentation  
**Timeline:** Complete within 1 week of issue creation
