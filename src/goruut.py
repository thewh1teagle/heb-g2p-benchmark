"""
uv pip install pygoruut
uv run src/goruut.py
"""
from lib.runner import run
from pygoruut.pygoruut import Pygoruut

_pygoruut = None


def phonemize(sentence):
    global _pygoruut
    if _pygoruut is None:
        _pygoruut = Pygoruut(version='v0.6.3')
    return str(_pygoruut.phonemize(language="Hebrew3", sentence=sentence))


if __name__ == "__main__":
    run(phonemize, "goruut")
