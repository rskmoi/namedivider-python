from typing import Dict
import pytest
from namedivider.divider.gbdt_name_divider import GBDTNameDivider
from namedivider.divider.config import NameDividerVersions


# Comment out until download functionality is implemented.
# name_test_data_v1 = \
#     [
#         ("菅義偉", {
#             "family": "菅", "given": "義偉", "separator": " ",
#             "score": 0.7300634880343344, "algorithm": "gbdt"
#         }),
#         ("阿部晋三", {
#             "family": "阿部", "given": "晋三", "separator": " ",
#             "score": 0.5761118242092244, "algorithm": "gbdt"
#         }),
#         ("中曽根康弘", {
#             "family": "中曽根", "given": "康弘", "separator": " ",
#             "score": 0.47535339308928076, "algorithm": "gbdt"
#         }),
#      ]
#
#
# @pytest.mark.parametrize("undivided_name, expect", name_test_data_v1)
# def test_divide_name_v1(undivided_name: str, expect: Dict):
#     name_divider = GBDTNameDivider.from_version(NameDividerVersions.GBDT_NAME_DIVIDER_V1)
#     divided_name = name_divider.divide_name(undivided_name)
#     assert divided_name.family == expect["family"]
#     assert divided_name.given == expect["given"]
#     assert divided_name.separator == expect["separator"]
#     assert divided_name.score == expect["score"]
#     assert divided_name.algorithm == expect["algorithm"]
#
#
# @pytest.mark.parametrize("undivided_name, expect", name_test_data_v1)
# def test_divide_name_latest(undivided_name: str, expect: Dict):
#     name_divider = GBDTNameDivider.from_version(NameDividerVersions.GBDT_NAME_DIVIDER_LATEST)
#     divided_name = name_divider.divide_name(undivided_name)
#     assert divided_name.family == expect["family"]
#     assert divided_name.given == expect["given"]
#     assert divided_name.separator == expect["separator"]
#     assert divided_name.score == expect["score"]
#     assert divided_name.algorithm == expect["algorithm"]
