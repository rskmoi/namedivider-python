# Performance Optimization Guide

## Introduction

NameDivider provides optimization techniques for efficiently processing thousands or even hundreds of thousands of Japanese names. This document explains performance improvement techniques when handling large datasets.

## Basic Optimization Techniques

### Cache Optimization

In name division processing, feature calculation takes up much of the processing time. The masks required for feature calculation are determined solely by the length of the full name and the character positions, regardless of character type. Therefore, by enabling `cache_mask=True`, you can cache mask calculations and achieve faster batch processing while maintaining complete accuracy.

```python
from namedivider import BasicNameDivider, BasicNameDividerConfig

# Enable caching
config = BasicNameDividerConfig(cache_mask=True)
divider = BasicNameDivider(config=config)

# Process large datasets
names = ["田中太郎", "佐藤花子", "田中次郎", ...]  # Thousands to tens of thousands of names
results = [divider.divide_name(name) for name in names]
```

**Effect**: Up to 10-20% speed improvement can be expected. However, Divider initialization time increases slightly, so it may be counterproductive in use cases where a new Divider instance is created for each request, such as in AWS Lambda.

### Algorithm Selection

It's important to choose the appropriate algorithm based on your use case:

| Algorithm | Accuracy | Speed | Use Case |
|-----------|----------|-------|----------|
| BasicNameDivider | 99.3%    | Fast | Primary processing of large datasets |
| GBDTNameDivider | 99.9%    | Moderate | When high accuracy is required |

```python
# For speed-focused use cases
basic_divider = BasicNameDivider()

# For accuracy-focused use cases
gbdt_divider = GBDTNameDivider()
```

## Rust Backend Utilization (Beta)

### Installation

```bash
pip install namedivider-core
```

### Usage

```python
from namedivider import BasicNameDivider, GBDTNameDivider, BasicNameDividerConfig, GBDTNameDividerConfig

# Use Rust backend with BasicNameDivider
basic_config = BasicNameDividerConfig(backend="rust")
rust_basic_divider = BasicNameDivider(config=basic_config)

# Use Rust backend with GBDTNameDivider
gbdt_config = GBDTNameDividerConfig(backend="rust")
rust_gbdt_divider = GBDTNameDivider(config=gbdt_config)
```

**Note**: `cache_mask=True` and `backend="rust"` cannot be used together. Specifying both will result in a validation error.

### Performance Comparison

Processing speed based on actual measurements with 10,000 names (names/sec):

| Algorithm | Python | Rust | Improvement |
|-----------|--------|------|-------------|
| BasicNameDivider | 4,152.8 | 18,597.7 | 4.5x |
| GBDTNameDivider | 1,143.3 | 6,277.4 | 5.5x |

**Important Notes**:
- Rust backend may fail to install in some environments
- If errors occur, we recommend using the Python backend

## Performance Measurement

You can use the benchmark scripts included in the project:

```bash
# Basic benchmark
bash scripts/benchmark_sample.sh

# Custom benchmark
python -m namedivider.cli benchmark your_test_file.txt --mode basic --backend rust
```

## Memory Optimization

Memory usage can be reduced by reusing objects:

```python
# Good example: Reuse divider object
divider = BasicNameDivider()
results = [divider.divide_name(name) for name in names]

# Bad example: Create new object each time
results = [BasicNameDivider().divide_name(name) for name in names]
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Rust Backend Installation Error

Since namedivider-core was released recently, there may be potential errors.

```
ERROR: Failed to install namedivider-core
```

**Solutions**:
- Use Python backend: `backend="python"`
- Consider disabling parallel processing as thread-safe processing may be incomplete

#### 2. Processing Speed Slower Than Expected

**Checkpoints**:
1. Is caching enabled?
2. Is the Rust backend correctly installed?
3. Are you creating new NameDivider instances every time?

```python
# Check configuration
config = BasicNameDividerConfig(backend="rust")
print(f"Backend: {config.backend}")
```

## Summary

Key points for optimizing performance for large-scale name processing with NameDivider:

1. **Cache Optimization**: Always effective when processing large numbers of names
2. **Rust Backend**: 4-6x speed improvement in compatible environments
3. **Memory Efficiency**: Reduce memory usage through object reuse

By combining these techniques, you can efficiently process hundreds of thousands of name records.