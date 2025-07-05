# NameDivider API 🦒

**⚠️ Important Notice**: The REST API implementation has been migrated to the [namedivider-rs repository](https://github.com/rskmoi/namedivider-rs) for further development and performance improvements.

[![Docker Pulls](https://img.shields.io/docker/pulls/rskmoi/namedivider-api.svg)](https://hub.docker.com/r/rskmoi/namedivider-api)
[![GitHub](https://img.shields.io/github/license/rskmoi/namedivider-rs)](https://github.com/rskmoi/namedivider-rs)

## 🆚 Legacy Python API

The previous Python-based API is available in the `./old/` directory for backward compatibility only. However, we strongly recommend using the new Rust-based API for better performance and reliability:

- **Up to 10x faster processing** with batch processing capabilities compared to Python implementation
- **Improved accuracy** with enhanced GBDT algorithm
- **Compatible with the original Python API (v0.1.0)**

---

## Current Rust-based API (Recommended)

A high-performance REST API for dividing Japanese full names into family names and given names, built with Rust for maximum efficiency.

## 🚀 Quick Start

### Installation

```bash
docker pull rskmoi/namedivider-api:0.3.0
```

### Run the API Server

```bash
docker run -d -p 8000:8000 rskmoi/namedivider-api:0.3.0
```

### Send HTTP Request

#### Using BasicNameDivider

```bash
curl -X POST -H "Content-Type: application/json" -d '{"names":["竈門炭治郎", "竈門禰豆子"]}' localhost:8000/divide
```

or

```bash
curl -X POST -H "Content-Type: application/json" -d '{"names":["竈門炭治郎", "竈門禰豆子"], "mode": "basic"}' localhost:8000/divide
```

#### Using GBDTNameDivider

```bash
curl -X POST -H "Content-Type: application/json" -d '{"names":["竈門炭治郎", "竈門禰豆子"], "mode": "gbdt"}' localhost:8000/divide
```

### Response

```json
{
    "divided_names":
        [
            {"family":"竈門","given":"炭治郎","separator":" ","score":0.3004587452426102,"algorithm":"kanji_feature"},
            {"family":"竈門","given":"禰豆子","separator":" ","score":0.30480429696983175,"algorithm":"kanji_feature"}
        ]
}
```

## 🎯 Features

### Two Division Algorithms

| Algorithm | Accuracy | Speed | Use Case |
|-----------|----------|-------|----------|
| **Basic Name Divider** | 99.3%    | Ultra Fast | High-volume processing, real-time applications |
| **GBDT Name Divider** | 99.9%    | Fast | Maximum accuracy requirements |

### Key Capabilities

- **🔥 High Performance**: Built with Rust for maximum throughput
- **📦 Containerized**: Ready-to-deploy Docker image
- **🌍 Multi-language Support**: Client samples for 7+ programming languages
- **⚡ Batch Processing**: Process up to 1,000 names per request
- **🎯 High Accuracy**: 99.9% accuracy with GBDT algorithm
- **🔧 Easy Integration**: RESTful API with JSON request/response

## 📡 API Endpoints

### POST /divide

Divide Japanese full names into family and given names.

**Request Body:**
```json
{
  "names": ["竈門炭治郎", "竈門禰豆子"],
  "mode": "basic"
}
```

**Response:**
```json
{
    "divided_names":
        [
            {"family":"竈門","given":"炭治郎","separator":" ","score":0.3004587452426102,"algorithm":"kanji_feature"},
            {"family":"竈門","given":"禰豆子","separator":" ","score":0.30480429696983175,"algorithm":"kanji_feature"}
        ]
}
```

**Parameters:**
- `names` (required): Array of undivided Japanese names (max 1,000 items)
- `mode` (optional): Division algorithm - "basic" (default) or "gbdt"

**Response Fields:**
- `family`: Family name portion
- `given`: Given name portion  
- `separator`: Separator character (always " ")
- `score`: Confidence score (0.0 - 1.0)
- `algorithm`: Algorithm used for division

## 🛠️ Client Libraries

We provide minimal client samples for multiple programming languages including TypeScript/JavaScript, Python, Go, PHP, Ruby, C#, and Kotlin.

For detailed examples and implementation code, please see: **[Client Samples](https://github.com/rskmoi/namedivider-rs/tree/main/api/client-samples)**
