#!/bin/bash
# Fix Mermaid Syntax Issues Script

set -e

echo "🔧 Fixing Mermaid syntax issues in documentation..."

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCS_DIR="$(dirname "$SCRIPT_DIR")/docs"

echo "📁 Searching in: $DOCS_DIR"

# Counter for processed files
count=0

# Find and fix encoded arrows in all markdown files
find "$DOCS_DIR" -name "*.md" -exec grep -l "mermaid" {} \; | while read -r file; do
    echo "🔍 Processing: $file"
    
    # Create backup
    cp "$file" "$file.bak"
    
    # Use sed for more reliable regex replacement within mermaid blocks
    awk '
        /^```mermaid$/ { in_mermaid = 1; print; next }
        /^```$/ && in_mermaid { in_mermaid = 0; print; next }
        in_mermaid {
            # Fix arrow syntax issues
            gsub(/--&gt;/, "-->");
            gsub(/--\\>/, "-->");
            gsub(/-&gt;&gt;/, "->>>");
            gsub(/-\\>\\>/, "->>>");
            gsub(/--&gt;&gt;/, "-->");
            gsub(/--\\>\\>/, "-->>>");
            # Fix double arrows
            gsub(/->>>/, "->>>");
            gsub(/-->>>/, "-->");
            # Fix common encoding issues
            gsub(/&amp;/, "&");
            gsub(/&lt;/, "<");
            gsub(/&gt;/, ">");
            gsub(/&quot;/, "\"");
        }
        { print }
    ' "$file.bak" > "$file"
    
    # Check if changes were made
    if ! cmp -s "$file" "$file.bak"; then
        echo "✅ Fixed: $file"
        ((count++))
    else
        echo "ℹ️  No changes: $file"
    fi
    
    # Remove backup
    rm "$file.bak"
done

echo "🚀 Mermaid syntax fix completed! Fixed $count files."
