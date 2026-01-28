"""
uv pip install phonemizer-fork espeakng-loader
uv run src/espeak_ng.py
"""
from lib.runner import run
from phonemizer.backend.espeak.wrapper import EspeakWrapper
from phonemizer import phonemize as _phonemize
import espeakng_loader

EspeakWrapper.set_library(espeakng_loader.get_library_path())
EspeakWrapper.set_data_path(espeakng_loader.get_data_path())


def phonemize(sentence):
    return _phonemize(sentence, language="he")


if __name__ == "__main__":
    run(phonemize, "espeak_ng")
