# NameDivider API

## About

NameDivider API is a Docker container that provides a RESTful API for dividing the Japanese full name into a family name and a given name.

I am developing NameDivider API to provide NameDivider functionality to non-Python language users.

## Installation

```
docker pull rskmoi/namedivider-api
```

## Usage

- Run Docker Image

```
docker run -d --rm -p 8000:8000 rskmoi/namedivider-api
```

- Send HTTP request

```
curl -X POST -H "Content-Type: application/json" -d '{"names":["竈門炭治郎", "竈門禰豆子"]}' localhost:8000/divide
```

- Response

```
{
    "divided_names":
        [
            {"family":"竈門","given":"炭治郎","separator":" ","score":0.3004587452426102,"algorithm":"kanji_feature"},
            {"family":"竈門","given":"禰豆子","separator":" ","score":0.30480429696983175,"algorithm":"kanji_feature"}
        ]
}
```

## NOTICE

- `names` is a list of undivided name. The maximum length of the list is 1000.
- If you require speed or want to use GBDTNameDivider, please try [v0.2.0-beta](https://github.com/rskmoi/namedivider-rs/tree/main/api).

