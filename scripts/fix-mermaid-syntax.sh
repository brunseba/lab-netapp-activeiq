#!/bin/bash
# Fix Mermaid Syntax Issues Script

echo "🔧 Fixing Mermaid syntax issues in documentation..."

DOCS_DIR="/Users/brun_s/Documents/veille-technologique/Professionel/donnees-d-entree/PE-AsProduct/netapp/docs"

# Find and fix encoded arrows in all markdown files
find "$DOCS_DIR" -name "*.md" -exec grep -l "mermaid" {} \; | while read -r file; do
    echo "🔍 Processing: $file"

    # Use perl for more reliable regex replacement
    perl -i -pe '
        if (/^```mermaid$/ .. /^```$/) {
            s/--&gt;/-->/g;
            s/--\\u003e/-->/g;
            s/-&gt;&gt;/->>>/g;
            s/-\\u003e\\u003e/->>>/g;
            s/--&gt;&gt;/-->>/g;
            s/--\\u003e\\u003e/-->>>/g;
        }
    ' "$file"

    echo "✅ Processed: $file"
done

echo "🚀 Mermaid syntax fix completed!"
