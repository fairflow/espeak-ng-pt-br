# CCS Test Logs

This directory contains test session logs from the CCS (Calculus of Communicating Systems) testing framework.

## Log Format

Each log file is named `ccs_test_session_YYYYMMDD_HHMMSS.json` and contains:

- **state_history**: Complete sequence of app states and user validations
- **bugs_found**: All bugs discovered during the session (manual + automated)
- **timing data**: Unix timestamps and intervals between transitions
- **mode tracking**: Which practice mode (FREE_TEXT, GUIDED_LIST, GUIDED_EDIT)
- **invariant violations**: Automatically detected inconsistencies

## Timing Analysis

Use the timing data to understand:
- Time spent between transitions (thinking, practicing, listening)
- Which modes users spend most time in
- Testing patterns (quick validation vs. deep exploration)

## Analysis Script

To analyze all logs:

```bash
cd /Users/matthew/Software/working/adaptive-text/espeak-ng
python3 << 'EOF'
import json
import glob

logs = sorted(glob.glob("ccs_test_logs/ccs_test_session*.json"))
for log_file in logs:
    with open(log_file) as f:
        data = json.load(f)
    print(f"{log_file}: {data['total_steps']} transitions, {len(data['bugs_found'])} bugs")
EOF
```

## Cleanup Policy

Keep recent logs for ongoing analysis. Archive or delete older logs once:
1. Bugs have been fixed
2. Timing patterns have been analyzed
3. Data has been summarized in reports

Do not delete logs that contain:
- Unresolved bugs
- Interesting timing patterns
- Edge cases or rare scenarios
