# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "renikud-onnx",
#     "tqdm",
# ]
#
# [tool.uv.sources]
# renikud-onnx = { git = "https://github.com/thewh1teagle/renikud-v4", subdirectory = "renikud-onnx" }
# ///

"""
wget https://huggingface.co/thewh1teagle/renikud/resolve/main/model.onnx -O renikud.onnx
uv run src/renikud.py
"""

from lib.runner import run
from renikud_onnx import G2P

_model = None


def phonemize(text):
    global _model
    if _model is None:
        _model = G2P("renikud.onnx")
    return _model.phonemize(text)


if __name__ == "__main__":
    run(phonemize, "renikud")
