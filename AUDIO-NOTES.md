# Audio Configuration Notes

## Current Setup

The build uses **pcaudiolib** for audio output, which was installed via MacPorts. This library has PulseAudio as a dependency, which causes harmless but annoying OpenGL-related dyld warnings on macOS.

### The Warnings (Now Suppressed)

```
dyld[xxxxx]: symbol '_CGLSetCurrentContext' missing from root...
dyld[xxxxx]: symbol '_CGLGetCurrentContext' missing from root...
dyld[xxxxx]: symbol '_gll_noop' missing from root...
```

These warnings are **cosmetic only** and don't affect functionality. They appear because PulseAudio dependencies have OpenGL references that aren't properly resolved on macOS.

## Solution Applied

The `run-espeak-ng` wrapper script now filters out these warnings using:
```bash
"$SCRIPT_DIR/espeak-ng" "$@" 2> >(grep -v "dyld\|libGL.dylib" >&2)
```

This keeps your terminal output clean while preserving any real error messages.

## Alternative Solutions

### Option 1: Use Native CoreAudio (Recommended for production)

If you want to eliminate these warnings entirely, you could build pcaudiolib from source with only CoreAudio support (no PulseAudio):

```bash
# Clone and build pcaudiolib without PulseAudio
git clone https://github.com/espeak-ng/pcaudiolib.git
cd pcaudiolib
./autogen.sh
./configure --prefix=/usr/local \
  --without-pulseaudio \
  --with-coreaudio
make
sudo make install

# Then rebuild espeak-ng
cd ../espeak-ng
make clean
./configure --prefix=$(pwd)/local \
  CPPFLAGS="-I/usr/local/include -I/opt/local/include" \
  LDFLAGS="-L/usr/local/lib -L/opt/local/lib"
make
make install
```

### Option 2: Disable Audio Output Entirely

If you don't need audio output (e.g., you're only generating phoneme transcriptions), you can build without pcaudiolib:

```bash
./configure --prefix=$(pwd)/local \
  --with-pcaudiolib=no \
  CPPFLAGS="-I/opt/local/include" \
  LDFLAGS="-L/opt/local/lib"
```

### Option 3: Set Environment Variable

You can also suppress the warnings system-wide by setting:
```bash
export DYLD_PRINT_WARNINGS=0
```

Add this to your `~/.zshrc` if desired.

## Audio Quality Notes

You mentioned the audio output is "robotic and unpleasant." This is normal for eSpeak-NG's default formant synthesis. Here are ways to improve quality:

### 1. Try Different Voices

```bash
# List all available voices
./local/bin/run-espeak-ng --voices

# Try different English variants
./local/bin/run-espeak-ng -v en-us "American English"
./local/bin/run-espeak-ng -v en-gb "British English"
./local/bin/run-espeak-ng -v en-scottish "Scottish English"

# Try different speaking rates
./local/bin/run-espeak-ng -s 150 "Slower speech"    # 150 words per minute
./local/bin/run-espeak-ng -s 200 "Faster speech"    # 200 words per minute
```

### 2. Adjust Pitch and Volume

```bash
# Lower pitch (sounds less robotic)
./local/bin/run-espeak-ng -p 30 "Lower pitch"

# Higher pitch
./local/bin/run-espeak-ng -p 60 "Higher pitch"

# Adjust amplitude (volume)
./local/bin/run-espeak-ng -a 150 "Louder"
```

### 3. Use MBROLA Voices (Better Quality)

MBROLA provides more natural-sounding voices but requires additional installation:

```bash
# Install MBROLA
sudo port install mbrola

# Download MBROLA voice data
# Visit: https://github.com/numediart/MBROLA-voices
```

### 4. Write to WAV File Instead of Playing

If you need better quality for processing, generate WAV files:

```bash
./local/bin/run-espeak-ng -w output.wav "Text to convert"
```

### 5. Alternative: Use macOS Built-in TTS

For better quality on macOS, you can use the built-in `say` command:

```bash
say "This uses macOS native voices"
say -v Samantha "Female voice"
say -v Alex "Male voice"

# List all available voices
say -v "?"

# Save to file
say -o output.aiff "Text to convert"
```

## Recommended Configuration

For the best experience with espeak-ng on macOS:

1. **Use the current setup** with warning suppression (already done)
2. **Experiment with different voices and parameters** to find acceptable quality
3. **Consider using macOS `say`** for production if quality is critical
4. **Use espeak-ng for phoneme generation** if that's your primary use case:
   ```bash
   ./local/bin/run-espeak-ng -x --ipa "text" # IPA phonemes
   ./local/bin/run-espeak-ng -x "text"       # eSpeak phonemes
   ```

## Performance Notes

The sonic library is included in your build, which allows for:
- Faster speech rates without pitch distortion
- Better audio quality at higher speeds
- Time-stretching capabilities

Test it:
```bash
./local/bin/run-espeak-ng -s 300 "Very fast speech with sonic"
```
