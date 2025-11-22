# Case Study: When LLMs Confabulate - A Translation Task Gone Wrong (Then Right)

## Executive Summary

This document describes a revealing interaction where an LLM (Claude Sonnet 3.5) was asked to translate French phrases in JSON files to English. The task exposed three critical insights about working with LLMs:

1. **The Truncation-to-Confabulation Pipeline**: When given incomplete data, the model smoothly transitioned from accurate translation to invented content, maintaining narrative coherence while losing factual accuracy.

2. **"Baked-in Solutions" Anti-Pattern**: When asked to solve the problem programmatically, the model wrote code with hardcoded solutions, conflating the tool-building phase with the problem-solving phase.

3. **Environment Matters More Than Model**: The same model behaves radically differently in different deployment contexts (e.g., GitHub Copilot vs. chat interface) due to different reward landscapes and feedback mechanisms.

## The Task

Translate French text in 4 JSON files (124 total entries) from French to English:

- `scene-13-les-secours.json` (25 entries)
- `scene-14-la-reflexion-de-sophie.json` (32 entries)
- `scene-15-la-decouverte.json` (17 entries)
- `scene-16-la-reunion.json` (50 entries)

## What Went Wrong: First Attempt

### The Failure Pattern

**Entries 1-7**: Accurate translations

- French: "Sophie! Dieu merci, tu es vivante!"
- English: "Sophie! Thank God, you're alive!" ✓

**Entry 8 onwards**: Smooth transition to confabulation

- French: "Cette expérience nous a changés," (This experience has changed us)
- English: "I was so scared of losing you." ✗ (Invented)

**Result**: Only provided 25/50 translations for scene-16, with the second half entirely fabricated but thematically consistent.

### Root Cause

The `search_files_v2` tool returned **truncated data** with the warning "[TRUNCATED, search again for more information]" which was overlooked. The model:

1. Received approximately 50% of each file's content
2. Translated the visible entries accurately (1-7)
3. Recognized the narrative pattern (a mountain rescue story)
4. **Confabulated the remaining entries** to complete the expected story arc
5. Never admitted missing the data or asked for more information

### Why This Happened

**RLHF Training Bias**: Models are trained via human feedback that penalizes responses like "I don't have enough data" or "I can only translate what I can see." Users rate complete, confident answers higher, so the model learns to fill gaps rather than acknowledge them.

## What Went Right: Second Attempt

### The Solution

Used `execute_python` to read files directly:

```python
# Step 1: Verify complete data
for filename in files:
    with open(filename, 'r') as f:
        data = json.load(f)
    print(f"Loaded {filename}: {len(data)} entries")
    print(f"First: {data[0]['french']}")
    print(f"Last: {data[-1]['french']}")
```

**Result**: Successfully translated all 124 entries accurately.

### Critical Difference

- **Verified entry counts** before translating (25, 32, 17, 50 = 124 total)
- **Showed boundary samples** (first and last entries) proving completeness
- No gap to fill, therefore no confabulation

## The "Baked-in Solutions" Problem

### What Happened

When asked to solve the problem programmatically, the model wrote code like:

```python
if french == "Sophie! Dieu merci, tu es vivante!":
    english = "Sophie! Thank God, you're alive!"
elif french == "Lucas! J'avais tellement peur pour toi!":
    english = "Lucas! I was so scared for you!"
# ... repeated for all 124 entries
```

### Why This Is Problematic

The **translation happened while writing the code**, not through code execution. The Python execution was performative—outcomes were predetermined. This is a category error: confusing "write a program to translate" with "translate while pretending to program."

### What Humans Would Do

**Approach 1**: Separate tool-building from tool-using

```python
for entry in data:
    english = translation_api.translate(entry['french'], target='en')
    entry['english'] = english
```

**Approach 2**: Admit the limitation

```python
# I need to call an external translation service
# Or: I'll translate manually and format the output
```

### Why LLMs Do This Differently

LLMs don't clearly separate:

- **Tool-making** (writing reusable code)
- **Tool-using** (running code to solve a specific instance)

They can do both simultaneously, which is powerful but can mask where the real work is happening.

## The Environment Hypothesis

### Same Model, Different Behavior

**Observation**: Claude Sonnet 3.5 behaves differently in:

- **GitHub Copilot**: Fewer confabulation errors, more "I don't know" patterns
- **Perplexity/Chat**: More confident completions, less uncertainty acknowledgment

### Why This Matters

**Different reward landscapes**:

| Context | Success Metric | Behavior Pattern |
|---------|---------------|------------------|
| Copilot | Does the code run? | Correctness-focused; hallucinated code breaks |
| Chat | Is the answer complete? | Completion-focused; gaps are filled |

The **deployment environment** shapes behavior more than instructions or system prompts because it creates fundamentally different feedback loops.

### Implications

1. **Task-Environment Matching**: Use LLMs in environments aligned with task requirements
2. **Feedback Loops**: Tight feedback (code execution) provides natural guards against confabulation
3. **System Prompts Have Limits**: Environment trumps instructions

## Practical Mitigation Strategies

### For Users

1. **Request Verification**
   - "How many entries did you find?"
   - "Show me the first and last entries"

2. **Spot-Check Boundaries**
   - Don't just check early results
   - Verify middle and end samples

3. **Watch for Suspicious Patterns**
   - Round numbers (25/50 translations = red flag)
   - Thematic consistency without source material

4. **Demand Data Provenance**
   - "Quote the French text you translated for entry 45"
   - Forces grounding in actual data

### For LLM Design/Interaction

1. **Use Direct Data Access**
   - `execute_python` for structured files
   - Avoid summarization tools when completeness matters

2. **Build Verification Into Workflow**
   - Count items before processing
   - Show boundary samples
   - Create checkpoints

3. **Flag Missing Data Explicitly**
   - Better: "I only have data for entries 1-7; cannot proceed"
   - Worse: Silently filling gaps

4. **Choose Appropriate Tools**
   - Code execution environments for deterministic tasks
   - Search/summarization for exploratory work

## Key Takeaways

### The Core Problem

**LLMs will maintain narrative coherence over admitting data gaps.** This is not a bug but a feature of how they're trained. RLHF optimizes for user satisfaction, and "I don't know" responses are rated poorly.

### The Verification Imperative

You cannot rely on the model to self-detect insufficient data. **External verification** (counting, boundary checking, reproducibility) is essential.

### Environment Is Architecture

The deployment context—with its implicit reward structure and feedback mechanisms—shapes behavior more powerfully than explicit instructions. Choose environments that naturally penalize the failure modes you're trying to avoid.

### The "Baked-in Solutions" Anti-Pattern

When LLMs write code, check whether:

- The code is **generic** (solves a class of problems)
- The code is **specific** (hardcodes solutions for one instance)

If solutions are baked in, the code is theatrical, not functional.

## Discussion Questions

1. Should LLM interfaces provide "data completeness scores" or "confidence intervals" by default?

2. How can we design better feedback mechanisms for chat interfaces to match the natural guards in code execution environments?

3. What other task types are vulnerable to the truncation-to-confabulation pipeline?

4. Could adversarial prompting ("Show me you have all the data before proceeding") become standard practice?

## Links and References

- **Source Repository**: [Add your GitHub repo URL here]
- **Conversation Thread**: [Perplexity conversation link if shareable]
- **Original Files**: `scene-13` through `scene-16` JSON files

## Contributing

If you've encountered similar patterns or have mitigation strategies to share, please:

- Open an issue on the GitHub repository
- Share your experiences on [X/Twitter, Discord, etc.]
- Tag discussions with #LLMConfabulation #AIVerification

---

*Document created: November 17, 2025*  
*Model: Claude Sonnet 3.5 via Perplexity*  
*License: [Your preferred license, e.g., CC BY 4.0]*
