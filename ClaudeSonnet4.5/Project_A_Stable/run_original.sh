#!/bin/bash
# Run tests for Stable Registration System

echo "Running Project A - Stable Implementation Tests"
echo "================================================"

# Run tests and capture output
python test_original.py 2>&1 | tee log_original.txt

# Capture timing information
echo "" >> time_original.txt
echo "Test execution completed at: $(date)" >> time_original.txt
echo "Exit code: $?" >> time_original.txt

echo ""
echo "Test execution complete. Check log_original.txt for details."
