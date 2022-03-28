# namedivider-python

![](https://badge.fury.io/py/namedivider-python.svg)
![](https://img.shields.io/pypi/pyversions/namedivider-python.svg)
![](https://github.com/rskmoi/namedivider-python/workflows/Python%20package/badge.svg)

**NameDivider** is a tool for dividing the Japanese full name into a family name and a given name.
```
input: 菅義偉 -> output: 菅 義偉
```

NameDivider divides the name using statistical information of the kanji used in the names.

In general names, the accuracy of division is about 99%. 

In rare names, the accuracy of division is about 92%.

## Documents

[NameDivider(日本語)](https://dune-fifth-da7.notion.site/NameDivider-9118f1a74ca545629dbbfa606a39ba0a "NameDivider")

## Installation
```
pip install namedivider-python
```

## Usage
It's simple to use.

```python
from namedivider import NameDivider
from pprint import pprint

divider = NameDivider()
divided_name = divider.divide_name("菅義偉")
print(divided_name)
# 菅 義偉
pprint(divided_name.to_dict())
# {'algorithm': 'kanji_feature',
# 'family': '菅',
# 'given': '義偉',
# 'score': 0.6328842762252201,
# 'separator': ' '}
```

## NameDivider API

NameDivider API is a Docker container that provides an API for dividing the Japanese full name into a family name and a given name.

It is being developed to provide NameDivider functions to those using languages other than Python.

### Installation

```
docker pull rskmoi/namedivider-api
```

### Usage

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

### Notice

- `names` is a list of undivided name. The maximum length of the list is 1000.

## CLI
Read namedivider/cli.py for more information.
```
$ nmdiv name 菅義偉
菅 義偉
$ nmdiv file undivided_names.txt
100%|███████████████████████████████████████████| 4/4 [00:00<00:00, 4194.30it/s]
原 敬
菅 義偉
阿部 晋三
中曽根 康弘
$ nmdiv accuracy divided_names.txt
100%|███████████████████████████████████████████| 5/5 [00:00<00:00, 3673.41it/s]
0.8
True: 滝 登喜男, Pred: 滝登 喜男
```

## Demo

`examples/example_streamlit.py` is an example of NameDivider with web UI.

The following command will launch the streamlit demo application locally.

```
pip install -y streamlit namedivider-python
streamlit run examples/example_streamlit.py
```


![example_streamlit](https://user-images.githubusercontent.com/26462938/159131355-3555a3aa-0b38-4a8a-9cd5-dad590746a6b.png)
