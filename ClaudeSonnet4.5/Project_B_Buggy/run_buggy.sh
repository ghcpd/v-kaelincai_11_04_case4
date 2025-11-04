#!/bin/bash
# Run tests for Buggy Registration System

echo "Running Project B - Buggy Implementation Tests"
echo "==============================================="

# Run tests and capture output
python test_buggy.py 2>&1 | tee log_buggy.txt

# Capture timing information
echo "" >> time_buggy.txt
echo "Test execution completed at: $(date)" >> time_buggy.txt
echo "Exit code: $?" >> time_buggy.txt

echo ""
echo "Test execution complete. Check log_buggy.txt for details."
