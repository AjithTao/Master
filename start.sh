#!/bin/bash

# Leadership Quality Tool - Root Launcher Script
# This script calls the actual startup script from the scripts folder

echo "🚀 Starting Leadership Quality Tool..."
echo "=================================="

# Check if scripts folder exists
if [ ! -d "scripts" ]; then
    echo "❌ Error: Scripts folder not found"
    echo "Please ensure you're running this from the project root directory"
    exit 1
fi

# Check if start.sh exists in scripts folder
if [ ! -f "scripts/start.sh" ]; then
    echo "❌ Error: start.sh not found in scripts folder"
    exit 1
fi

echo "📁 Found startup script in scripts folder"
echo "🔄 Launching application..."

# Call the actual startup script
bash scripts/start.sh
