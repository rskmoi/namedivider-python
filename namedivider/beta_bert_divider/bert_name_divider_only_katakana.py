import json
from pathlib import Path
from typing import Tuple, Union

import torch  # type: ignore
from transformers import BertForSequenceClassification, PretrainedConfig  # type: ignore

from namedivider.divider.divided_name import DividedName

CURRENT_DIR = Path(__file__).resolve().parent


class BERTNameDividerOnlyKatakana:
    """
    Divider with deep learning model.
    Names consisting only of katakana characters are accepted.
    """

    def __init__(self, model_path: Union[str, Path], separator: str = " ", family_first: bool = False):
        """
        :param model_path: Path for BERT model
        :param separator: Character for separate family name and given name
        :param family_first: whether family name comes first
        """
        self.separator = separator
        self.family_first = family_first

        # Prepare model
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        config = PretrainedConfig.from_json_file(CURRENT_DIR / "config.json")
        model = BertForSequenceClassification(config=config)
        model.load_state_dict(torch.load(model_path, map_location=torch.device(self.device)))
        self.model = model.to(self.device).eval()

        # Prepare vocabularies
        with open(CURRENT_DIR / "vocab.json") as f:
            vocab_hash = json.load(f)
        self.vocab_hash = vocab_hash

    def preprocess(self, undivided_name: str) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Preprocess undivided name.

        :param undivided_name: Names with no space between the family name and given name
        :return: [preprocessed_names, attention_masks]
          preprocessed_names: Tensor of preprocessed names. Names are tokenized and convert into ids.
          attention_masks: Tensor of attention masks.
          https://huggingface.co/docs/transformers/glossary#attention-mask
        """
        preprocessed_names = []
        attention_masks = []
        for i in range(1, len(undivided_name)):
            candidate = undivided_name[:i] + "・" + undivided_name[i:]
            tagged = ["[CLS]"] + list(candidate) + ["[SEP]"]
            padded = tagged + ["[PAD]"] * (16 - len(tagged))
            attn_mask = [1] * len(tagged) + [0] * (16 - len(tagged))
            preprocessed_names.append([self.vocab_hash[c] for c in padded])
            attention_masks.append(attn_mask)

        return (
            torch.Tensor(preprocessed_names).type(torch.int32).to(self.device),
            torch.Tensor(attention_masks).type(torch.int32).to(self.device),
        )

    def divide_name(self, undivided_name: str) -> DividedName:
        """
        Divide undivided name.
        The reason divider.name_divider_base._NameDivider is not inherited is that
        batch inference must be done for computational speed.

        :param undivided_name: Names with no space between the family name and given name
        :return: Divided name
        """
        preprocessed_names, attention_masks = self.preprocess(undivided_name)
        with torch.no_grad():
            res = self.model(input_ids=preprocessed_names, attention_mask=attention_masks).logits
            scores = torch.softmax(res, dim=0)[:, 1]
            score = torch.max(scores).cpu().numpy()
            max_idx = torch.argmax(scores).cpu().numpy()

        if self.family_first:
            family = undivided_name[: max_idx + 1]
            given = undivided_name[max_idx + 1 :]
        else:
            family = undivided_name[max_idx + 1 :]
            given = undivided_name[: max_idx + 1]
        return DividedName(
            family=family,
            given=given,
            separator=self.separator,
            score=float(score),
            algorithm="beta_bert_only_katakana",
        )
