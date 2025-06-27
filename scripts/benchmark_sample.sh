#!/bin/bash

# Sample benchmark script using hyperfine
# Replace 'test_names.txt' with your test file

hyperfine \
    --warmup 2 \
    --runs 10 \
    "nmdiv benchmark test_names_sample.txt --mode basic --no-mask-cache --silent" \
    "nmdiv benchmark test_names_sample.txt --mode basic --use-mask-cache --silent" \
    "nmdiv benchmark test_names_sample.txt --mode basic --no-mask-cache --backend rust --silent" \
    "nmdiv benchmark test_names_sample.txt --mode gbdt --no-mask-cache --silent" \
    "nmdiv benchmark test_names_sample.txt --mode gbdt --use-mask-cache --silent" \
    "nmdiv benchmark test_names_sample.txt --mode gbdt --no-mask-cache --backend rust --silent" \