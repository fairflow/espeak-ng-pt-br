#!/bin/bash
# Configuration script for macOS with MacPorts libraries

# MacPorts installs libraries in /opt/local by default
# This script configures espeak-ng to find pcaudiolib and sonic

./configure \
  --prefix=/usr/local \
  CPPFLAGS="-I/opt/local/include" \
  LDFLAGS="-L/opt/local/lib" \
  "$@"
