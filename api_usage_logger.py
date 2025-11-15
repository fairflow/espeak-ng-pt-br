"""
API Usage Logger - Track TTS API calls for cost monitoring

Logs all TTS API calls to a JSON file for cost analysis.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Log file location (outside git, in home directory)
LOG_FILE = Path.home() / ".miolingo" / "api_usage.json"

def ensure_log_dir():
    """Create log directory if it doesn't exist"""
    LOG_FILE.parent.mkdir(exist_ok=True)

def log_api_call(
    api_type: str,  # "google_cloud_tts", "gtts", "espeak"
    text: str,
    language: str,
    char_count: int,
    audio_bytes: Optional[int] = None,
    success: bool = True,
    error: Optional[str] = None,
    cached: bool = False
):
    """
    Log an API call for cost tracking
    
    Args:
        api_type: Which TTS API was used
        text: The text that was synthesized
        language: Language code
        char_count: Number of characters synthesized
        audio_bytes: Size of generated audio in bytes (if available)
        success: Whether the call succeeded
        error: Error message if failed
        cached: Whether this was served from cache (no API cost)
    """
    ensure_log_dir()
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "api_type": api_type,
        "text": text[:50] + "..." if len(text) > 50 else text,  # Truncate for privacy
        "language": language,
        "char_count": char_count,
        "audio_bytes": audio_bytes,
        "success": success,
        "error": error,
        "cached": cached
    }
    
    # Append to log file
    logs = []
    if LOG_FILE.exists():
        try:
            with open(LOG_FILE, 'r') as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            logs = []
    
    logs.append(entry)
    
    with open(LOG_FILE, 'w') as f:
        json.dump(logs, f, indent=2)

def get_usage_stats(days: int = 30) -> Dict:
    """
    Get usage statistics for the last N days
    
    Returns dict with:
        - total_calls: Total API calls
        - by_api: Breakdown by API type
        - by_language: Breakdown by language
        - total_chars: Total characters processed
        - cached_calls: Number of cached responses (no cost)
        - estimated_costs: Cost estimates per API
    """
    ensure_log_dir()
    
    if not LOG_FILE.exists():
        return {"error": "No usage data found"}
    
    with open(LOG_FILE, 'r') as f:
        logs = json.load(f)
    
    # Filter by date
    from datetime import timedelta
    cutoff = datetime.now() - timedelta(days=days)
    recent_logs = [
        log for log in logs 
        if datetime.fromisoformat(log['timestamp']) > cutoff
    ]
    
    # Calculate stats
    stats = {
        "total_calls": len(recent_logs),
        "by_api": {},
        "by_language": {},
        "total_chars": 0,
        "cached_calls": 0,
        "billable_calls": 0,
        "failed_calls": 0
    }
    
    for log in recent_logs:
        api = log['api_type']
        lang = log['language']
        
        # Count by API
        if api not in stats['by_api']:
            stats['by_api'][api] = {"calls": 0, "chars": 0}
        stats['by_api'][api]['calls'] += 1
        stats['by_api'][api]['chars'] += log['char_count']
        
        # Count by language
        if lang not in stats['by_language']:
            stats['by_language'][lang] = 0
        stats['by_language'][lang] += 1
        
        # Total chars
        stats['total_chars'] += log['char_count']
        
        # Cached vs billable
        if log['cached']:
            stats['cached_calls'] += 1
        else:
            stats['billable_calls'] += 1
        
        # Failed calls
        if not log['success']:
            stats['failed_calls'] += 1
    
    # Estimate costs (Google Cloud TTS pricing: $4 per 1M chars)
    stats['estimated_costs'] = {}
    
    for api, data in stats['by_api'].items():
        if api == 'google_cloud_tts':
            # $4 per 1M characters (standard voices)
            cost = (data['chars'] / 1_000_000) * 4.0
            stats['estimated_costs'][api] = f"${cost:.4f}"
        elif api == 'gtts':
            # Free but rate limited
            stats['estimated_costs'][api] = "$0.00 (free, rate limited)"
        elif api == 'espeak':
            # Free and local
            stats['estimated_costs'][api] = "$0.00 (local)"
    
    # Cache efficiency
    if stats['total_calls'] > 0:
        cache_hit_rate = (stats['cached_calls'] / stats['total_calls']) * 100
        stats['cache_hit_rate'] = f"{cache_hit_rate:.1f}%"
    
    return stats

if __name__ == "__main__":
    # CLI usage
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "stats":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        stats = get_usage_stats(days)
        
        print(f"\n📊 API Usage Stats (Last {days} days)")
        print("=" * 60)
        print(f"Total API calls: {stats['total_calls']}")
        print(f"Billable calls: {stats['billable_calls']}")
        print(f"Cached calls: {stats['cached_calls']} ({stats.get('cache_hit_rate', 'N/A')})")
        print(f"Failed calls: {stats['failed_calls']}")
        print(f"Total characters: {stats['total_chars']:,}")
        
        print("\n🔊 By API Type:")
        for api, data in stats['by_api'].items():
            print(f"  {api}: {data['calls']} calls, {data['chars']:,} chars")
        
        print("\n🌍 By Language:")
        for lang, count in stats['by_language'].items():
            print(f"  {lang}: {count} calls")
        
        print("\n💰 Estimated Costs:")
        for api, cost in stats['estimated_costs'].items():
            print(f"  {api}: {cost}")
        
        print("\n" + "=" * 60)
    else:
        print("Usage: python api_usage_logger.py stats [days]")
        print("Example: python api_usage_logger.py stats 7")
