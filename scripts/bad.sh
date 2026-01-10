#!/bin/bash

# Test file with intentional ShellCheck issues for static_analysis.yml validation
# This should trigger SC2086: Double quote to prevent globbing and word splitting

FILES="file1.txt file2.txt file3.txt"

for f in $FILES; do
    echo $f
done
