#!/bin/bash

# Profile performance with scalene - CLI summary comparison
echo "=== Basic v0.3 Python ==="
scalene --cli --cpu-percent-threshold 1 -m namedivider.cli --- benchmark test_names_sample.txt --mode basic --backend python --no-mask-cache --silent

echo "=== Basic v0.4 Python ==="
scalene --cli --cpu-percent-threshold 1 -m namedivider.cli --- benchmark test_names_sample.txt --mode basic --backend python --use-mask-cache --silent

echo -e "\n=== Basic v0.4 Rust ==="
scalene --cli --cpu-percent-threshold 1 -m namedivider.cli --- benchmark test_names_sample.txt --mode basic --backend rust --no-mask-cache --silent

echo -e "\n=== GBDT v0.3 Python ==="
scalene --cli --cpu-percent-threshold 1 -m namedivider.cli --- benchmark test_names_sample.txt --mode gbdt --backend python --no-mask-cache --silent

echo -e "\n=== GBDT v0.4 Python ==="
scalene --cli --cpu-percent-threshold 1 -m namedivider.cli --- benchmark test_names_sample.txt --mode gbdt --backend python --use-mask-cache --silent

echo -e "\n=== GBDT v0.4 Rust ==="
scalene --cli --cpu-percent-threshold 1 -m namedivider.cli --- benchmark test_names_sample.txt --mode gbdt --backend rust --no-mask-cache --silent