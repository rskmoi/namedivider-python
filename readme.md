# NameDivider-Python
## About
NameDivider is a tool for dividing Japanese name, which is connected family name and given name.
```
input: 菅義偉 -> output: 菅 義偉
```
I plan to release version 0.1 by the end of November 2020...

## USAGE
```
from name_divider import NameDivider

name_divider = NameDivider()
divided_name = name_divider.divide_name("菅義偉")
print(divided_name)
# 菅 義偉
print(divided_name.to_dict())
# {'family': '菅', 'given': '義偉', 'separator': ' ', 'score': 0.7482349894384595, 'algorithm': 'kanji_feature'}
```

## TODO

### MUST

- [x] Implementation
- [x] Add comments
- [ ] Add tests
- [ ] Write readme.md and other document.
- [ ] Preparing for distribution as a Python library

### BETTER

- [ ] Add examples