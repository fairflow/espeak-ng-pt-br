# Testing Guide for Miolingo Multi-Language Pronunciation Trainer

**Version 1.3.4** | For App Users & Testers

Thank you for helping us improve Miolingo! This guide explains how you can help test the app and report any problems you find.

---

## 🎯 Why Your Testing Helps

You don't need to be a programmer to help test! As a language learner, you're the perfect person to tell us:

- What's confusing or unclear
- What doesn't work as expected
- What features would be helpful
- What makes the app frustrating to use

**Your feedback makes the app better for everyone!**

---

## 🧪 What to Test

### Basic Functionality

Please try these and let us know if anything goes wrong:

#### 1. Audio Playback
- [ ] Click the 🔊 Speak button - does audio play?
- [ ] **iPhone users**: Try with WAV toggle ON and OFF
- [ ] Can you hear the pronunciation clearly?
- [ ] Does it sound natural?

#### 2. Recording
- [ ] Click the 🎤 Record button - does it record?
- [ ] Does it stop after the correct number of seconds?
- [ ] Do you see the "Processing..." message?
- [ ] Does it show results after recording?

#### 3. Scoring
- [ ] Practice a word you know well - is the score reasonable?
- [ ] Try the same word 3 times - are scores consistent?
- [ ] Try deliberately mispronouncing - does the score go down?
- [ ] Do perfect matches show 100%?

#### 4. Settings
- [ ] Change recording duration - does it save?
- [ ] **iPhone users**: Toggle WAV audio - does it save automatically?
- [ ] Change speech speed - does it affect playback?
- [ ] Click "Save Settings" - can you reload the page and settings persist?

#### 5. Practice Modes
- [ ] Quick Practice - works with short words?
- [ ] Sentence Practice - works with long phrases?
- [ ] File Upload - can you upload a .txt file?
- [ ] File Practice - does "Next" button work?

#### 6. Statistics & History
- [ ] Do practice counts increase correctly?
- [ ] Can you see past practice sessions?
- [ ] Can you expand/collapse session details?
- [ ] Are scores displayed correctly?

---

## 📱 Device-Specific Testing

### If You Have an iPhone

Please test specifically:

1. **Audio Playback**
   - Try with WAV toggle OFF - what happens?
   - Try with WAV toggle ON - does it work better?
   - Does the toggle setting save when you reload the page?

2. **Safari Browser**
   - Does the app load correctly in Safari?
   - Can you grant microphone permission?
   - Does recording work in Safari?

3. **Chrome Browser (iPhone)**
   - Same tests as Safari
   - Note any differences

### If You Have an Android Phone

Please test:

1. **Chrome Browser**
   - Audio playback working?
   - Recording working?
   - Are results accurate?

2. **Other Browsers**
   - Try Firefox or Samsung Internet
   - Report what works or doesn't

### If You're on Desktop/Laptop

Please test:

1. **Different Browsers**
   - Try Chrome, Firefox, Safari, Edge
   - Report which works best

2. **Microphone Options**
   - Try built-in mic
   - Try headset mic
   - Note quality differences

---

## 🐛 How to Report a Bug

When something doesn't work, please tell us:

### What to Include

1. **What you were trying to do**
   - Example: "I clicked the Speak button to hear 'casa'"

2. **What you expected to happen**
   - Example: "I expected to hear the pronunciation"

3. **What actually happened**
   - Example: "Nothing played, the button just grayed out"

4. **Your device & browser**
   - Example: "iPhone 13, Safari" or "Windows laptop, Chrome"

5. **Steps to reproduce** (if you can repeat the problem)
   - Example: "Happens every time I click Speak with WAV toggle OFF"

### Bug Report Template

Copy this template and fill it out:

```
**Problem**: [Brief description]

**Steps to reproduce**:
1. [First thing you did]
2. [Next thing you did]
3. [What triggered the problem]

**Expected behavior**: [What should have happened]

**Actual behavior**: [What actually happened]

**Device**: [iPhone 14 / Samsung Galaxy / MacBook / etc.]

**Browser**: [Safari / Chrome / Firefox / etc.]

**App Version**: 1.0.0

**Settings** (if relevant):
- Language: [Portuguese/French/Dutch/Flemish]
- Voice/Dialect: [e.g., pt-br, fr-fr, nl, etc.]
- WAV audio: [ON/OFF]
- Recording duration: [X seconds]
- Other relevant settings

**Additional notes**: [Anything else that might help]
```

### Where to Send Bug Reports

**Email**: io@miolingo.io

**Discord**: [Link will be added soon for community testing]

**GitHub Issues**: For technical users comfortable with GitHub

---

## 💡 Feature Suggestions

Have an idea to make the app better? We'd love to hear it!

### Good Feature Requests Include:

1. **The problem you're trying to solve**
   - Example: "I keep forgetting which words I struggle with"

2. **Your proposed solution**
   - Example: "Show a list of my lowest-scoring words"

3. **Why it would help you**
   - Example: "So I can focus practice on problem areas"

### Feature Request Template

```
**Feature**: [Short name for your idea]

**The problem**: [What difficulty are you facing?]

**Proposed solution**: [How would you like it to work?]

**Why it helps**: [How would this improve your learning?]

**Priority** (for you): [Nice to have / Would be helpful / Really need this]
```

---

## 🧪 Systematic Testing Checklist

Want to do thorough testing? Work through this checklist:

### First-Time User Experience

- [ ] App loads without errors
- [ ] Initial page is clear/understandable
- [ ] Microphone permission request appears (if needed)
- [ ] Default settings are reasonable
- [ ] Tutorial or help is visible/findable

### Quick Practice Mode

- [ ] Type a word → Speak works
- [ ] Record button is visible
- [ ] Recording countdown appears
- [ ] Results show up after recording
- [ ] Score makes sense
- [ ] Can practice multiple words in a row

### Sentence Practice Mode

- [ ] Longer phrases work
- [ ] Auto-duration calculation is reasonable
- [ ] Results handle long text correctly
- [ ] Phoneme display is readable

### File Upload Practice

- [ ] Can select a .txt file
- [ ] File uploads successfully
- [ ] First phrase appears
- [ ] "Next" button works
- [ ] Progress indicator is accurate
- [ ] Can practice all phrases in file

### Settings Persistence

- [ ] Change a setting
- [ ] Click "Save Settings"
- [ ] Reload the page
- [ ] Setting is still changed

### Statistics Accuracy

- [ ] Practice a few words
- [ ] Check "Current Session" stats
- [ ] Numbers match what you did
- [ ] Try "View Statistics" button
- [ ] All-time stats look reasonable

### History Review

- [ ] Find "Session History"
- [ ] See your recent practices
- [ ] Expand a session
- [ ] Details are correct
- [ ] Can collapse it again

### Audio Settings (iPhone)

- [ ] WAV toggle OFF → test audio
- [ ] WAV toggle ON → test audio
- [ ] Which one works better?
- [ ] Does toggle setting save?

### Error Handling

- [ ] Try recording with no microphone
- [ ] Try very short recording (1 sec) with long phrase
- [ ] Try empty text input
- [ ] Upload a non-.txt file
- [ ] Does app show helpful error messages?

---

## 📊 What Makes a Good Test

### ✅ Good Testing Practice

- **Test one thing at a time** - easier to identify the problem
- **Try it multiple times** - make sure it's consistent
- **Note the details** - exact wording of errors, exact steps
- **Test on your actual device** - not just what you think will work
- **Test like a new user** - pretend you've never seen the app before

### ❌ Less Helpful Testing

- "Something doesn't work" (too vague)
- Testing only on one device
- Not noting what you did before the problem
- Assuming problems are your fault (they're usually not!)

---

## 🎓 Common Issues to Watch For

Based on feedback so far, please especially test:

### Known Issue: iPhone Audio
- WAV toggle should save automatically (v0.9.1 fix)
- Confirm this works for you

### Known Issue: Microphone Permission
- First-time users might miss the permission request
- Note if the app guides you through this clearly

### Known Issue: Recording Too Short
- Default 3 seconds might be too short for some phrases
- Try adjusting and note if it helps

### Known Issue: Background Noise
- Noisy environments cause poor recognition
- Test in different noise levels, note difference

---

## 🤝 Testing as a Team

If you're testing with others:

### Coordinate Your Testing

- Each person test different devices/browsers
- Share your bug reports with each other
- Don't duplicate the same bug report
- If someone reports a bug, try to reproduce it

### Testing Party Ideas

- Everyone tests the same word list
- Compare scores and consistency
- Note any differences between devices
- Have fun with it!

---

## 📈 Advanced Testing (Optional)

For power users who want to help more:

### Stress Testing

- Upload a file with 100+ phrases
- Practice continuously for 30 minutes
- Note any slowdowns or crashes

### Edge Cases

- Very long sentences (20+ words)
- Very short words (2-3 letters)
- Words with special characters (ção, ã)
- Rapid clicking of buttons
- Changing settings mid-practice

### Browser Console (Technical)

If you're comfortable with it:
1. Press F12 (or Cmd+Option+I on Mac)
2. Go to "Console" tab
3. Look for red error messages
4. Copy them into your bug report

---

## 🌟 Thank You!

Your testing helps make the app better for all language learners. Every bug report, feature suggestion, and test result is valuable!

**Remember**: 
- There are no stupid questions
- Every bug you find helps improve the app
- Your perspective as a learner is exactly what we need

---

## Quick Testing Reference

| **Test This** | **Look For** |
|---------------|--------------|
| Audio playback | Plays clearly, no errors |
| Recording | Records correct duration, processes |
| Scoring | Reasonable scores, consistent |
| Settings | Save correctly, persist after reload |
| WAV toggle (iPhone) | Saves automatically, improves audio |
| File upload | Accepts .txt, shows all phrases |
| Statistics | Accurate counts and scores |
| History | Shows all sessions, expandable |
| Different devices | Works on your phone/computer |
| Different browsers | Works in Safari/Chrome/Firefox |

---

*For technical/development testing (CCS framework), see [CCS_TESTING_README.md](../CCS_TESTING_README.md)*

*For general app usage, see [USER_GUIDE.md](USER_GUIDE.md)*

*App Version 0.9.1*
