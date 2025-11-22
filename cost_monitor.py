#!/usr/bin/env python3
"""
Cost Monitoring Dashboard - View API usage and costs

Run this script to see real-time API usage statistics and cost estimates.
"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import sys

# Log file location
LOG_FILE = Path.home() / ".miolingo" / "api_usage.json"

def format_cost(amount):
    """Format cost with color coding"""
    if amount == 0:
        return f"\033[32m${amount:.4f}\033[0m"  # Green for free
    elif amount < 0.10:
        return f"\033[33m${amount:.4f}\033[0m"  # Yellow for cheap
    else:
        return f"\033[31m${amount:.4f}\033[0m"  # Red for expensive

def show_dashboard(days=30):
    """Display cost monitoring dashboard"""
    if not LOG_FILE.exists():
        print("❌ No usage data found. API logger may not be running.")
        print(f"   Expected log file: {LOG_FILE}")
        return
    
    with open(LOG_FILE, 'r') as f:
        logs = json.load(f)
    
    # Filter by date
    cutoff = datetime.now() - timedelta(days=days)
    recent_logs = [
        log for log in logs 
        if datetime.fromisoformat(log['timestamp']) > cutoff
    ]
    
    if not recent_logs:
        print(f"❌ No usage data in last {days} days")
        return
    
    # Calculate statistics
    stats = {
        'total_calls': len(recent_logs),
        'by_api': defaultdict(lambda: {'calls': 0, 'chars': 0, 'bytes': 0}),
        'by_language': defaultdict(int),
        'by_date': defaultdict(int),
        'cached_calls': 0,
        'failed_calls': 0,
        'total_chars': 0
    }
    
    for log in recent_logs:
        api = log['api_type']
        lang = log['language']
        date = log['timestamp'][:10]  # YYYY-MM-DD
        
        stats['by_api'][api]['calls'] += 1
        stats['by_api'][api]['chars'] += log['char_count']
        if log.get('audio_bytes'):
            stats['by_api'][api]['bytes'] += log['audio_bytes']
        
        stats['by_language'][lang] += 1
        stats['by_date'][date] += 1
        stats['total_chars'] += log['char_count']
        
        if log.get('cached'):
            stats['cached_calls'] += 1
        if not log.get('success', True):
            stats['failed_calls'] += 1
    
    # Display dashboard
    print("\n" + "="*70)
    print(f"  💰  MIOLINGO API COST MONITORING DASHBOARD  💰")
    print(f"      Last {days} days • Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*70)
    
    # Summary
    print(f"\n📊 SUMMARY")
    print(f"  Total API Calls: {stats['total_calls']:,}")
    print(f"  Total Characters: {stats['total_chars']:,}")
    billable = stats['total_calls'] - stats['cached_calls']
    print(f"  Billable Calls: {billable:,} (Cached: {stats['cached_calls']:,})")
    if stats['failed_calls'] > 0:
        print(f"  ⚠️  Failed Calls: {stats['failed_calls']}")
    
    # By API
    print(f"\n🔊 BY API TYPE")
    print(f"  {'API':<20} {'Calls':<10} {'Chars':<12} {'Audio (MB)':<12} {'Est. Cost'}")
    print(f"  {'-'*20} {'-'*10} {'-'*12} {'-'*12} {'-'*10}")
    
    total_cost = 0
    for api, data in sorted(stats['by_api'].items()):
        audio_mb = data['bytes'] / (1024 * 1024) if data['bytes'] > 0 else 0
        
        # Calculate cost
        if api == 'google_cloud_tts':
            # $4 per 1M characters
            cost = (data['chars'] / 1_000_000) * 4.0
            total_cost += cost
            cost_str = format_cost(cost)
        elif api == 'gtts':
            cost_str = format_cost(0) + " (rate limited)"
        else:  # espeak
            cost_str = format_cost(0) + " (local)"
        
        print(f"  {api:<20} {data['calls']:<10,} {data['chars']:<12,} {audio_mb:<12.2f} {cost_str}")
    
    print(f"  {'-'*20} {'-'*10} {'-'*12} {'-'*12} {'-'*10}")
    print(f"  {'TOTAL':<20} {'':<10} {'':<12} {'':<12} {format_cost(total_cost)}")
    
    # By Language
    print(f"\n🌍 BY LANGUAGE")
    for lang, count in sorted(stats['by_language'].items(), key=lambda x: -x[1]):
        pct = (count / stats['total_calls']) * 100
        print(f"  {lang:<10} {count:>6,} calls ({pct:>5.1f}%)")
    
    # Daily trend (last 7 days)
    print(f"\n📈 DAILY TREND (Last 7 days)")
    recent_dates = sorted(stats['by_date'].keys())[-7:]
    for date in recent_dates:
        count = stats['by_date'][date]
        bar = "█" * (count // 5) if count > 0 else ""
        print(f"  {date}  {count:>4,} calls  {bar}")
    
    # Cache efficiency
    if stats['total_calls'] > 0:
        cache_rate = (stats['cached_calls'] / stats['total_calls']) * 100
        print(f"\n⚡ CACHE EFFICIENCY")
        print(f"  Hit Rate: {cache_rate:.1f}%")
        print(f"  Saved: {stats['cached_calls']:,} API calls")
        if cache_rate < 50:
            print(f"  💡 Tip: Low cache rate. Consider increasing TTL or checking phrase diversity.")
    
    # Cost projection
    if billable > 0:
        daily_avg = billable / days
        monthly_projection = daily_avg * 30
        monthly_cost = (monthly_projection * stats['total_chars'] / stats['total_calls'] / 1_000_000) * 4.0
        
        print(f"\n💸 COST PROJECTION")
        print(f"  Daily Avg: {daily_avg:.1f} calls")
        print(f"  Monthly Est: {monthly_projection:.0f} calls")
        print(f"  Monthly Cost: {format_cost(monthly_cost)}")
        
        if monthly_cost > 1.0:
            print(f"  ⚠️  Warning: Projected cost exceeds $1/month")
        elif monthly_cost > 5.0:
            print(f"  🚨 ALERT: Projected cost exceeds $5/month! Review usage.")
    
    print("\n" + "="*70 + "\n")

def show_alerts():
    """Check for cost/usage alerts"""
    if not LOG_FILE.exists():
        return
    
    with open(LOG_FILE, 'r') as f:
        logs = json.load(f)
    
    # Check last 24 hours
    cutoff = datetime.now() - timedelta(hours=24)
    recent = [l for l in logs if datetime.fromisoformat(l['timestamp']) > cutoff]
    
    alerts = []
    
    # High volume alert (>100 calls/day)
    if len(recent) > 100:
        alerts.append(f"⚠️  High volume: {len(recent)} calls in last 24h")
    
    # Failed calls
    failed = sum(1 for l in recent if not l.get('success', True))
    if failed > 10:
        alerts.append(f"⚠️  High failure rate: {failed} failed calls")
    
    # Cost spike
    google_chars = sum(l['char_count'] for l in recent if l['api_type'] == 'google_cloud_tts')
    daily_cost = (google_chars / 1_000_000) * 4.0
    if daily_cost > 0.50:
        alerts.append(f"🚨 Cost spike: ${daily_cost:.2f} in last 24h")
    
    if alerts:
        print("\n⚠️  ALERTS:")
        for alert in alerts:
            print(f"   {alert}")
        print()

if __name__ == "__main__":
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    
    try:
        show_dashboard(days)
        show_alerts()
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard closed\n")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
