"""
wget https://huggingface.co/thewh1teagle/phonikud-onnx/resolve/main/phonikud-1.0.int8.onnx
uv pip install phonikud phonikud-onnx tqdm
uv run src/phonikud_model.py
"""
from lib.runner import run
from phonikud_onnx import Phonikud
from phonikud import phonemize as _phonemize

_model = Phonikud("./phonikud-1.0.int8.onnx")


def phonemize(sentence):
    vocalized = _model.add_diacritics(sentence)
    return _phonemize(vocalized)


if __name__ == "__main__":
    run(phonemize, "phonikud")
