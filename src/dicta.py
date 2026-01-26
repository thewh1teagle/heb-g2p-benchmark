"""
uv pip install -U dicta-onnx

wget https://github.com/thewh1teagle/dicta-onnx/releases/download/model-files-v1.0/dicta-1.0.int8.onnx
uv run src/dicta.py
"""

from lib.runner import run
from dicta_onnx import Dicta
from phonikud import phonemize as phonemize_phonikud

_model = None


def phonemize(text):
    global _model
    if _model is None:
        _model = Dicta("dicta-1.0.int8.onnx")

    with_diacritics = _model.add_diacritics(text)
    return phonemize_phonikud(with_diacritics)


if __name__ == "__main__":
    run(phonemize, "dicta")
