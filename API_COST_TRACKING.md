# API Cost Tracking System

Monitors TTS API usage and costs for Miolingo to prevent unexpected bills.

## Files

- **api_usage_logger.py** - Logs every API call with character counts
- **cost_monitor.py** - Dashboard to view usage statistics and costs

## Usage

### View Cost Dashboard

```bash
python cost_monitor.py        # Last 30 days
python cost_monitor.py 7      # Last 7 days
```

### Dashboard Shows:
- Total API calls (billable vs cached)
- Character counts per API
- Estimated costs (Google Cloud TTS: $4/1M chars)
- Daily trends
- Cache hit rate
- Monthly cost projections
- Alerts for high volume or cost spikes

### Log Location

All data is stored in `~/.miolingo/api_usage.json` (outside git for privacy/security)

## Pricing Reference

| API | Cost | Notes |
|-----|------|-------|
| Google Cloud TTS | $4 per 1M chars | Standard voices |
| gTTS | Free | Unofficial, rate limited, 429 errors |
| eSpeak NG | Free | Local synthesis, robotic |

## Cost Optimization

1. **Caching is critical** - 24h cache reduces API calls by 95%+
2. **Monitor cache hit rate** - Should be >80% for stable phrase sets
3. **Watch for spikes** - Alert if >$0.50/day (=$15/month)
4. **Typical usage** - 200 unique phrases = $0.003 (with caching)

## Alerts

The dashboard will warn you if:
- Daily cost exceeds $0.50
- Call volume exceeds 100/day
- Failure rate is high (>10 failures/day)
- Monthly projection exceeds $1

## Example Output

```
=====================================================================
  💰  MIOLINGO API COST MONITORING DASHBOARD  💰
=====================================================================

📊 SUMMARY
  Total API Calls: 245
  Total Characters: 8,543
  Billable Calls: 48 (Cached: 197)

🔊 BY API TYPE
  API                  Calls      Chars        Audio (MB)   Est. Cost
  -------------------- ---------- ------------ ------------ ----------
  google_cloud_tts     48         8,543        1.23         $0.0342
  espeak               0          0            0.00         $0.0000
  gtts                 0          0            0.00         $0.0000 (rate limited)

💸 COST PROJECTION
  Daily Avg: 1.6 calls
  Monthly Est: 48 calls
  Monthly Cost: $0.0342
```

## Integration

The logging is automatically enabled in `app.py` (v1.3.5+). Every TTS call is logged before caching, so you can track:
- How many unique phrases are generated
- Which APIs are actually being used
- Cost trends over time

No configuration needed - just run the dashboard script anytime to check costs!
