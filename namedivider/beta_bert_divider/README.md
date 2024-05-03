# Divide name with BERT models

## NOTICE
All source code in this directory is in beta version, 

and there is a high likelihood of disruptive changes without backward compatibility in the future.

## WHY USE BERT
Previously, the algorithm was designed to handle only Japanese names containing kanji characters. 

However, to accommodate a wider range of situations, I have decided to target names composed entirely of katakana.

Since the previous algorithm couldn't address this situation, I have opted to introduce a Deep Learning model.

## USAGE

### installation

1. install libraries

```
pip install torch>=2.3.0 transformers>=4.40.1
```

2. download model

```
wget https://github.com/rskmoi/namedivider-python/releases/download/beta_bert/bert_katakana_v0_3_0.pt
```

### how to use

```python
from namedivider import GBDTNameDivider
from namedivider.beta_bert_divider import BERTNameDividerOnlyKatakana, CombinedNameDivider

divider = CombinedNameDivider(
    base_divider=GBDTNameDivider(), 
    katakana_divider=BERTNameDividerOnlyKatakana("./bert_katakana_v0_3_0.pt") # path to the downloaded model
)

divider.divide_name("フランシスコザビエル")
# DividedName(family='ザビエル', given='フランシスコ', separator=' ', score=0.9906243681907654, algorithm='beta_bert_only_katakana')
```

## ACCURACY AND SPEED

- Accuracy
  
Measuring the accuracy using a privately held data set, the accuracy is 88.28%.

- Speed

| environment | Speed |
----|---- 
| With GPU (NVIDIA GeForce RTX 3090) | 1,000records / 11secs |
| Without GPU | 1,000records / 77secs |
