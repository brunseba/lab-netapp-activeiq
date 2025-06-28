#!/bin/bash

# Documentation Server Startup Script
# Run this script to start the NetApp ActiveIQ MCP Server documentation

echo "🚀 Starting NetApp ActiveIQ MCP Server Documentation..."
echo "📋 Activating virtual environment..."
echo "📚 Using MkDocs v1.6.1 with Material theme v9.6.14"
echo "🎨 Using Mermaid.js v11.4.0 for advanced diagrams..."

# Check if virtual environment exists
if [ ! -d "venv-docs" ]; then
    echo "❌ Virtual environment not found. Creating new environment..."
    python3 -m venv venv-docs
    echo "📦 Installing documentation dependencies..."
    venv-docs/bin/pip install -r requirements-docs.txt
fi

echo "🌐 Starting development server..."
echo "🔗 Documentation will be available at: http://127.0.0.1:8000"
echo "⚡ Live reload enabled - changes will be reflected automatically"
echo ""
echo "📝 Press Ctrl+C to stop the server"
echo ""

# Start the MkDocs development server
venv-docs/bin/mkdocs serve

echo ""
echo "👋 Documentation server stopped."
