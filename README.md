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

## Installation
```
pip install namedivider-python
```

## USAGE
It's simple to use.

```python
from namedivider import NameDivider
from pprint import pprint

name_divider = NameDivider()
divided_name = name_divider.divide_name("菅義偉")
print(divided_name)
# 菅 義偉
pprint(divided_name.to_dict())
# {'algorithm': 'kanji_feature',
# 'family': '菅',
# 'given': '義偉',
# 'score': 0.6328842762252201,
# 'separator': ' '}
```

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
