"""
wget https://github.com/thewh1teagle/nakdimon-onnx/releases/download/v0.1.0/nakdimon.onnx
uv pip install nakdimon-onnx
uv run src/nakdimon.py
"""
from lib.runner import run
from nakdimon_onnx import Nakdimon
from phonikud import phonemize as phonemize_phonikud

_model = None


def phonemize(text):
    global _model
    if _model is None:
        _model = Nakdimon("nakdimon.onnx")

    with_diacritics = _model.compute(text)
    return phonemize_phonikud(with_diacritics)


if __name__ == "__main__":
    run(phonemize, "nakdimon")
