#!/bin/bash
# Update IPA transcriptions using espeak-ng
# Usage: ./update_ipa.sh

if ! command -v espeak-ng &> /dev/null; then
    echo "Error: espeak-ng not found. Please install it first."
    exit 1
fi

echo "Updating IPA transcriptions for French phrases..."
echo "This will take a few moments..."

# Function to get IPA from espeak-ng
get_ipa() {
    local text="$1"
    espeak-ng -v fr-fr --ipa -q "$text" 2>/dev/null | tr -d '\n'
}

# Process each phrase file
for level_dir in phrases-*; do
    if [ -d "$level_dir" ]; then
        echo "Processing $level_dir..."
        for file in "$level_dir"/*.txt; do
            if [ -f "$file" ]; then
                # Create temporary file
                temp_file="${file}.tmp"
                
                # Process each line
                while IFS='|' read -r phrase translation ipa; do
                    # Trim whitespace
                    phrase=$(echo "$phrase" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
                    translation=$(echo "$translation" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
                    
                    # Get real IPA
                    real_ipa=$(get_ipa "$phrase")
                    
                    # Write updated line
                    echo "$phrase | $translation | [$real_ipa]" >> "$temp_file"
                done < "$file"
                
                # Replace original file
                mv "$temp_file" "$file"
                echo "  ✓ Updated $file"
            fi
        done
    fi
done

echo "✓ IPA transcriptions updated!"
