#!/usr/bin/env python3
"""
record_audio.py - Simple audio recorder for pronunciation practice

Usage:
    # Record 3 seconds
    python3 record_audio.py -o recording.wav
    
    # Record 5 seconds
    python3 record_audio.py -o recording.wav -d 5
    
    # Test microphone
    python3 record_audio.py --test
"""

import argparse
import sys

try:
    import sounddevice as sd
    import soundfile as sf
    import numpy as np
except ImportError as e:
    print(f"Error: {e}")
    print("\nPlease activate the virtual environment:")
    print("  source venv/bin/activate")
    sys.exit(1)


def list_devices():
    """List available audio devices"""
    print("\n🎤 Available audio devices:\n")
    print(sd.query_devices())


def test_microphone(duration=2):
    """Test microphone recording"""
    print(f"\n🎤 Testing microphone...")
    print(f"Recording {duration} seconds...")
    print("Speak now!")
    
    recording = sd.rec(
        int(duration * 16000),
        samplerate=16000,
        channels=1,
        dtype='float32'
    )
    sd.wait()
    
    print("✓ Recording complete")
    print("\n🔊 Playing back...")
    sd.play(recording, 16000)
    sd.wait()
    print("✓ Playback complete\n")


def record_audio(output_file, duration=3, samplerate=16000):
    """Record audio to file"""
    print(f"\n🎤 Recording to: {output_file}")
    print(f"Duration: {duration} seconds")
    print("Speak now!")
    print()
    
    recording = sd.rec(
        int(duration * samplerate),
        samplerate=samplerate,
        channels=1,
        dtype='float32'
    )
    
    # Progress indicator
    for i in range(duration):
        print(f"  {'█' * (i + 1)}{'░' * (duration - i - 1)} {i + 1}s")
        sd.sleep(1000)
    
    sd.wait()
    
    print(f"\n✓ Recording complete")
    print(f"💾 Saving to {output_file}...")
    
    sf.write(output_file, recording, samplerate)
    print("✓ Saved successfully\n")


def main():
    parser = argparse.ArgumentParser(
        description="Record audio for pronunciation practice"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output WAV file"
    )
    parser.add_argument(
        "-d", "--duration",
        type=int,
        default=3,
        help="Recording duration in seconds (default: 3)"
    )
    parser.add_argument(
        "-r", "--rate",
        type=int,
        default=16000,
        help="Sample rate (default: 16000)"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test microphone (record and playback)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available audio devices"
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_devices()
    elif args.test:
        test_microphone(duration=args.duration)
    elif args.output:
        record_audio(args.output, duration=args.duration, samplerate=args.rate)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
