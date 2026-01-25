"""
wget https://huggingface.co/thewh1teagle/phonikud-onnx/resolve/main/phonikud-1.0.int8.onnx
uv pip install phonikud-onnx
uv run src/phonikud_naive.py
"""
from lib.runner import run
from phonikud_onnx import Phonikud
from lib.naive_phonemizer import phonemize as naive_phonemize

_model = None


def phonemize(text):
    global _model
    if _model is None:
        _model = Phonikud("phonikud-1.0.int8.onnx")

    with_diacritics = _model.add_diacritics(text)
    return naive_phonemize(with_diacritics)


if __name__ == "__main__":
    run(phonemize, "phonikud_naive")
