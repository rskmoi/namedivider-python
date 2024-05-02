# namedivider-python
<div align="center">
    <img src="https://user-images.githubusercontent.com/26462938/170857814-75d609ad-6c4a-48ed-98a6-318943521a2f.png" alt="logo"/>
</div>
<div align="center">
    <img src="https://badge.fury.io/py/namedivider-python.svg" alt=""/>
    <img src="https://img.shields.io/pypi/pyversions/namedivider-python.svg" alt=""/>
    <img src="https://github.com/rskmoi/namedivider-python/workflows/Python%20package/badge.svg" alt=""/>
</div>

---

**NameDivider** is a tool for dividing the Japanese full name into a family name and a given name.
```
input: 菅義偉 -> output: 菅 義偉
```

NameDivider divides the name using statistical information of the kanji used in the names.

Measuring the accuracy using a privately held data set, the accuracy is 99.91%.

You can see how it works with [this demo](https://share.streamlit.io/rskmoi/namedivider-python/examples/demo/example_streamlit.py "Demo").

## Documents

[NameDivider(日本語)](https://dune-fifth-da7.notion.site/NameDivider-9118f1a74ca545629dbbfa606a39ba0a "NameDivider")

## Installation
```
pip install namedivider-python
```

## Usage
It's simple to use.

```python
from namedivider import BasicNameDivider, GBDTNameDivider
from pprint import pprint

basic_divider = BasicNameDivider() # BasicNameDivider is fast but accuracy is 99.2%
divided_name = basic_divider.divide_name("菅義偉")

gbdt_divider = GBDTNameDivider() # GBDTNameDivider is slow but accuracy is 99.9%
divided_name = gbdt_divider.divide_name("菅義偉")

print(divided_name)
# 菅 義偉

pprint(divided_name.to_dict())
# {'algorithm': 'kanji_feature',
# 'family': '菅',
# 'given': '義偉',
# 'score': 0.7300634880343344,
# 'separator': ' '}
```

For more advanced features, see [here](docs/advanced_features.md).

## NameDivider API

NameDivider API is a Docker container that provides a RESTful API for dividing the Japanese full name into a family name and a given name.

I am developing NameDivider API to provide NameDivider functionality to non-Python language users.

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
- If you require speed or want to use GBDTNameDivider, please try [v0.2.0-beta](https://github.com/rskmoi/namedivider-rs/tree/main/api).

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

## License

### Source code and gbdt_model_v1.txt
MIT License

### bert_katakana_v0_3_0.pt
cc-by-sa-4.0

### family_name_repository.pickle

- English

(1) Purpose of use

family_name_repository.pickle is available for commercial/non-commercial use if you use this software to divide name, and to develop algorithms for dividing name.

Any other use of family_name_repository.pickle is prohibited.

(2) Liability

The author or copyright holder assumes no responsibility for the software.

- Japanese

(1) 利用目的

このソフトウェアを用いて姓名分割、および姓名分割アルゴリズムの開発をする場合、family_name_repository.pickleは商用/非商用問わず利用可能です。

それ以外の目的でのfamily_name_repository.pickleの利用を禁じます。

(2) 責任

作者または著作権者は、family_name_repository.pickleに関して一切の責任を負いません。

The family name data used in family_name_repository.pickle is provided by Myoji-Yurai.net(名字由来net).

![](https://user-images.githubusercontent.com/26462938/170855242-84ec7418-b288-4b64-bbc2-4927776493bf.png)

## Ongoing Projects

- Porting Python to Rust

https://github.com/rskmoi/namedivider-rs
