# eSpeak-NG Local Build - Quick Reference

## Installation Summary

✅ **Successfully built and installed eSpeak-NG locally with full audio support**

### Build Configuration
- **Installation prefix**: `./local/` (within the repository)
- **Audio support**: pcaudiolib ✓
- **Speed optimization**: sonic ✓
- **MacPorts libraries**: Configured via CPPFLAGS and LDFLAGS

### Why Local Installation?

This avoids conflicts with the system-installed espeak from MacPorts:
```bash
# Old version (MacPorts)
/opt/local/bin/espeak --version
# espeak 1.48.04

# New version (this build)
./local/bin/run-espeak-ng --version
# eSpeak NG text-to-speech: 1.52-dev
```

## Quick Start

### Run a test
```bash
./local/bin/run-espeak-ng "Hello, this is eSpeak NG with audio support"
```

### List available voices
```bash
./local/bin/run-espeak-ng --voices
```

### Use different voices
```bash
./local/bin/run-espeak-ng -v en-us "American English"
./local/bin/run-espeak-ng -v en-gb "British English"
./local/bin/run-espeak-ng -v es "Spanish"
```

## Configuration Files

- **configure-macos.sh** - Helper script for configuring with MacPorts paths
- **local/** - Installation directory
- **local/README.md** - Detailed usage documentation

## Rebuilding

To rebuild after source changes:
```bash
make clean
./configure-macos.sh
make
make install
```

## Integration with Your Project

If you want to use this build in your project, you have several options:

### 1. Direct invocation
```bash
/Users/matthew/Software/working/adaptive-text/espeak-ng/local/bin/run-espeak-ng "$text"
```

### 2. Add to PATH (in your project script or shell)
```bash
export PATH="/Users/matthew/Software/working/adaptive-text/espeak-ng/local/bin:$PATH"
export DYLD_LIBRARY_PATH="/Users/matthew/Software/working/adaptive-text/espeak-ng/local/lib:/opt/local/lib"
export ESPEAK_DATA_PATH="/Users/matthew/Software/working/adaptive-text/espeak-ng/local/share/espeak-ng-data"

espeak-ng "Your text here"
```

### 3. Use libespeak-ng library
If your project is in C/C++, link against the library:
```bash
gcc -I/Users/matthew/Software/working/adaptive-text/espeak-ng/local/include \
    -L/Users/matthew/Software/working/adaptive-text/espeak-ng/local/lib \
    -lespeak-ng yourprogram.c
```

## Troubleshooting

### If you get "library not found" errors
Make sure `DYLD_LIBRARY_PATH` includes both the local lib and MacPorts:
```bash
export DYLD_LIBRARY_PATH="$(pwd)/local/lib:/opt/local/lib"
```

### If voices are not found
Set the data path:
```bash
export ESPEAK_DATA_PATH="$(pwd)/local/share/espeak-ng-data"
```

### To verify audio support
```bash
otool -L local/lib/libespeak-ng.1.dylib | grep -E "(pcaudio|sonic)"
```

Should show:
```
/opt/local/lib/libpcaudio.0.dylib
/opt/local/lib/libsonic.dylib
```

## Documentation Updates

Updated `docs/building.md` to include:
- MacPorts installation instructions
- Configure command with proper CPPFLAGS and LDFLAGS
- Reference to configure-macos.sh helper script
