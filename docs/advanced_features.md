# Advanced Features

Here are some more advanced features that are not mentioned in the readme.md.

## Customize rule-based algorithms

You can customize rule-based algorithms.

### Preset Rules

I have prepared an algorithm that registers specific family and given names in advance and divides along them.

The following uses BasicNameDivider, but the same can be done with GBDTNameDivider.

```python
from namedivider import BasicNameDivider, BasicNameDividerConfig, SpecificFamilyNameRule, SpecificGivenNameRule

config = BasicNameDividerConfig(
    custom_rules=[
        SpecificFamilyNameRule(family_names=["竜胆",]),
        SpecificGivenNameRule(given_names=["木綿子"]),
    ]
)
divider = BasicNameDivider(config=config)

divider.divide_name("竜胆尊")
# DividedName(family='竜胆', given='尊', separator=' ', score=1.0, algorithm='rule_specific_family')
divider.divide_name("浜木綿子")
# DividedName(family='浜', given='木綿子', separator=' ', score=1.0, algorithm='rule_specific_given')
```

### Original Rules

You can even create your own rules!

The following is an example of a rule to process a name that was already divided by separator.

```python
from typing import Optional
from namedivider import BasicNameDivider, BasicNameDividerConfig
from namedivider.divider.divided_name import DividedName
from namedivider.rule.rule import Rule

class AlreadyExistsSeparatorRule(Rule):
    def __init__(self):
        pass
    
    def divide(self, undivided_name: str, separator: str = " ") -> Optional[DividedName]:
        if separator in undivided_name:
            divided_name_str = undivided_name.split(separator)
            return DividedName(
                family=divided_name_str[0],
                given=divided_name_str[-1],
                separator=separator,
                score=1.0,
                algorithm="rule_already_divided",
            )

config = BasicNameDividerConfig(custom_rules=[AlreadyExistsSeparatorRule()])
divider = BasicNameDivider(config=config)
divider.divide_name("菅 義偉")
# DividedName(family='菅', given=' 義偉', separator=' ', score=1.0, algorithm='rule_already_divided')
```

## Divide names consisting entirely of katakana

Although in beta, plans are in progress to split such names by using a deep learning model.

[readme.md](../namedivider/beta_bert_divider/README.md)
