#!/bin/bash
# Setup script for Buggy Registration System

echo "Setting up Project B - Buggy Implementation (Post-Regression)"
echo "=============================================================="

# Check Python version
python --version

# Install dependencies (none required for this project, but keeping for consistency)
if [ -f "requirements_buggy.txt" ]; then
    pip install -r requirements_buggy.txt
fi

echo "Setup complete for Buggy Version"
