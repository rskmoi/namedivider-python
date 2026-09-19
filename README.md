# namedivider-python🦒

<div align="center">
    <img src="https://user-images.githubusercontent.com/26462938/170857814-75d609ad-6c4a-48ed-98a6-318943521a2f.png" alt="NameDivider Logo" width="600"/>
    
[![PyPI version](https://badge.fury.io/py/namedivider-python.svg)](https://badge.fury.io/py/namedivider-python)
[![Python versions](https://img.shields.io/pypi/pyversions/namedivider-python.svg)](https://pypi.org/project/namedivider-python/)
[![PyPI downloads](https://img.shields.io/pypi/dm/namedivider-python.svg)](https://pypi.org/project/namedivider-python/)
[![CI](https://github.com/rskmoi/namedivider-python/workflows/Python%20package/badge.svg)](https://github.com/rskmoi/namedivider-python/actions)

**NameDivider is a tool that divides Japanese full names into family and given names.**

[🚀 Try Live Demo](https://share.streamlit.io/rskmoi/namedivider-python/examples/demo/example_streamlit.py) • [📖 Documentation (日本語)](https://dune-fifth-da7.notion.site/NameDivider-9118f1a74ca545629dbbfa606a39ba0a) • [🐳 Docker API](https://hub.docker.com/r/rskmoi/namedivider-api) • [⚡ Rust Version](https://github.com/rskmoi/namedivider-rs)

</div>

---

## 💡 Why NameDivider?

Japanese full names like "菅義偉" are typically stored as single strings with no clear boundary between family and given names. NameDivider solves this with exceptional accuracy.

Unlike cloud-based AI solutions, NameDivider processes all data locally — no external API calls, no data transmission, and full privacy control.

```python
# Before
person_name = "菅義偉"  # How do you know where to divide?

# After  
from namedivider import BasicNameDivider
divider = BasicNameDivider()
result = divider.divide_name("菅義偉")
print(f"Family: {result.family}, Given: {result.given}")
# Family: 菅, Given: 義偉
```

### ✨ Key Features

- 🎯 **99.91% accuracy** - Tested on real-world Japanese names
- ⚡ **Multiple algorithms** - Choose between speed (Basic) or accuracy (GBDT)
- 🔐 **Privacy-first** – Local-only processing, ideal for sensitive data
- 🔧 **Production ready** - CLI, Python library, and Docker support
- 🎨 **Interactive demo** - Try it live with Streamlit
- 📊 **Confidence scoring** - Know when to trust the results
- 🛠️ **Customizable rules** - Add domain-specific patterns

## 🚀 Quick Start

### Installation

Requires Python 3.10 or later.

```bash
pip install namedivider-python
```

### Basic Usage

```python
from namedivider import BasicNameDivider, GBDTNameDivider

# Fast but good accuracy (99.3%)
basic_divider = BasicNameDivider()
result = basic_divider.divide_name("菅義偉")
print(result)  # 菅 義偉

# Slower but best accuracy (99.9%)
gbdt_divider = GBDTNameDivider()
result = gbdt_divider.divide_name("菅義偉")
print(result.to_dict())
# {
#   'algorithm': 'gbdt',
#   'family': '菅',
#   'given': '義偉',
#   'score': 0.7300634880343344,
#   'separator': ' '
# }
```

## 🔧 Multiple Interfaces

### 🖥️ Command Line Interface

Perfect for batch processing and automation:

```bash
# Single name
$ nmdiv name 菅義偉
菅 義偉

# Process file with progress bar
$ nmdiv file customer_names.txt
100%|██████████| 1000/1000 [00:02<00:00, 431.2it/s]

# Check accuracy on labeled data
$ nmdiv accuracy test_data.txt
Accuracy: 99.1%
```

### 🐳 REST API (Docker)

For environments where Python cannot be used, we provide a containerized REST API:

```bash
# Run the API server
docker run -d -p 8000:8000 rskmoi/namedivider-api

# Send batch requests
curl -X POST localhost:8000/divide \
  -H "Content-Type: application/json" \
  -d '{"names": ["竈門炭治郎", "竈門禰豆子"]}'
```

**Response:**
```json
{
  "divided_names": [
    {"family": "竈門", "given": "炭治郎", "separator": " ", "score": 0.3004587452426102, "algorithm": "kanji_feature"},
    {"family": "竈門", "given": "禰豆子", "separator": " ", "score": 0.30480429696983175, "algorithm": "kanji_feature"}
  ]
}
```

### 🎯 Interactive Web Demo

Try NameDivider instantly in your browser: **[Live Demo →](https://share.streamlit.io/rskmoi/namedivider-python/examples/demo/example_streamlit.py)**

Run locally:
```bash
cd examples/demo
pip install -r requirements.txt
streamlit run example_streamlit.py
```

## 📊 Performance & Benchmarks

| Algorithm                         | Accuracy | Speed (names/sec)  | Use Case |
|-----------------------------------|----------|--------------------|----------|
| BasicNameDivider / backend=python | 99.3%    | 4152.8             | Stable & compatible |
| BasicNameDivider / backend=rust   | 99.3%    | 18597.7            | Max performance (if available) |
| GBDTNameDivider / backend=python  | 99.9%    | 1143.3 | Best accuracy, guaranteed |
| GBDTNameDivider / backend=rust    | 99.9%    | 6277.4 | Fast + accurate (if available) |

Run your own benchmarks:
```bash
bash scripts/benchmark_sample.sh
```

## 🛠️ Advanced Features

### Custom Rules

Handle domain-specific names with custom patterns:

```python
from namedivider import BasicNameDivider, BasicNameDividerConfig
from namedivider import SpecificFamilyNameRule

config = BasicNameDividerConfig(
    custom_rules=[
        SpecificFamilyNameRule(family_names=["竜胆"]),  # Rare family names
    ]
)
divider = BasicNameDivider(config=config)
result = divider.divide_name("竜胆尊")
# DividedName(family='竜胆', given='尊', separator=' ', score=1.0, algorithm='rule_specific_family')
```

### Speed Up

For high-volume processing, NameDivider offers several optimization options:

```python
from namedivider import BasicNameDivider, BasicNameDividerConfig

# Load your names
with open("names.txt", "r", encoding="utf-8") as f:
    names = [line.strip() for line in f]

# Option 1: Enable caching (faster repeated processing)
config = BasicNameDividerConfig(cache_mask=True)
divider = BasicNameDivider(config=config)
results = [divider.divide_name(name) for name in names]

# Option 2: (beta) Use Rust backend (up to 4x faster)
# First install: pip install namedivider-core
config = BasicNameDividerConfig(backend="rust")
divider = BasicNameDivider(config=config)
results = [divider.divide_name(name) for name in names]
```

## 🏢 Typical Use Cases

- **Customer Data Processing** - Clean and standardize name databases
- **Form Validation** - Real-time name splitting in web applications  
- **Analytics & Reports** - Generate family name statistics
- **Data Migration** - Convert legacy systems with combined name fields
- **Government & Municipal** - Process citizen registration data
- **Security-sensitive Environments** - Process names **without sending data to external APIs**


## 📚 Examples & Tutorials

- [🌐 Use REST API with minimal client samples](namedivider-api/) - Integration examples (7 languages available in [namedivider-rs](https://github.com/rskmoi/namedivider-rs))
- [⚡ Performance Optimization](docs/performance_optimization.md) - Handle large datasets efficiently
- [🔧 Custom Rules Examples](docs/advanced_features.md) - Domain-specific configurations


## 📄 License

### Source code and gbdt_model_v1.txt
MIT License

### bert_katakana_v0_3_0.pt
cc-by-sa-4.0

### family_name_repository.pickle

**English**

(1) Purpose of use

family_name_repository.pickle is available for commercial/non-commercial use if you use this software to divide name, and to develop algorithms for dividing name.

Any other use of family_name_repository.pickle is prohibited.

(2) Liability

The author or copyright holder assumes no responsibility for the software.

**Japanese / 日本語**

(1) 利用目的

このソフトウェアを用いて姓名分割、および姓名分割アルゴリズムの開発をする場合、family_name_repository.pickleは商用/非商用問わず利用可能です。

それ以外の目的でのfamily_name_repository.pickleの利用を禁じます。

(2) 責任

作者または著作権者は、family_name_repository.pickleに関して一切の責任を負いません。

The family name data used in family_name_repository.pickle is provided by Myoji-Yurai.net(名字由来net).

![](https://user-images.githubusercontent.com/26462938/170855242-84ec7418-b288-4b64-bbc2-4927776493bf.png)

## 🔗 Related Projects

- [⚡ namedivider-rs](https://github.com/rskmoi/namedivider-rs) - High-performance Rust implementation
- [🧠 BERT Katakana Divider](namedivider/beta_bert_divider/) - Deep learning approach for katakana names

## 📈 Project Stats

<div align="center">

![GitHub stars](https://img.shields.io/github/stars/rskmoi/namedivider-python?style=social)
![GitHub forks](https://img.shields.io/github/forks/rskmoi/namedivider-python?style=social)
![Docker Pulls](https://img.shields.io/docker/pulls/rskmoi/namedivider-api.svg)

**Trusted by developers worldwide**

</div>

---

<div align="center">
Made with ❤️ by <a href="https://github.com/rskmoi">@rskmoi</a> • Contact <a href="https://x.com/rskmoi">@rskmoi</a>
</div>
