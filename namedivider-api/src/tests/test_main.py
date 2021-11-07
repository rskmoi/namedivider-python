from fastapi.testclient import TestClient
from main import app
import pytest


client = TestClient(app)


def test_health():
    res = client.get("/health")
    assert res.status_code == 200


def test_valid_names():
    _json = {"names": ["菅義偉", "安倍晋三"]}
    res = client.post("/divide", json=_json)
    divided_names = res.json()["divided_names"]

    answers = [
        {'family': '菅', 'given': '義偉', 'separator': ' ', 'score': 0.6328842762252201, 'algorithm': 'kanji_feature'},
        {'family': '安倍', 'given': '晋三', 'separator': ' ', 'score': 0.45186276187760605, 'algorithm': 'kanji_feature'}
    ]

    for _name, _answer in zip(divided_names, answers):
        assert _name["family"] == _answer["family"]
        assert _name["given"] == _answer["given"]
        assert _name["separator"] == _answer["separator"]
        assert _name["score"] == _answer["score"]
        assert _name["algorithm"] == _answer["algorithm"]


def test_over_1000():
    names = []
    for i in range(1001):
        names.append("菅義偉")
    print(len(names))
    _json = {"names": names}
    res = client.post("/divide", json=_json)
    assert res.status_code == 422


def test_invalid_names():
    _json = {"names": ["菅義偉", "安"]}
    res = client.post("/divide", json=_json)
    assert res.status_code == 422