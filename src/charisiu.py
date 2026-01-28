"""
uv pip install transformers torch
uv run src/charisiu.py
"""
from lib.runner import run
from transformers import T5ForConditionalGeneration, AutoTokenizer
import torch

_model = None
_tokenizer = None


def phonemize(sentence):
    global _model, _tokenizer
    if _model is None or _tokenizer is None:
        _model = T5ForConditionalGeneration.from_pretrained('charsiu/g2p_multilingual_byT5_small_100')
        _tokenizer = AutoTokenizer.from_pretrained('google/byt5-small')

    words = sentence.split()
    words = ['<heb-il>: ' + i for i in words]

    with torch.no_grad():
        out = _tokenizer(words, padding=True, add_special_tokens=False, return_tensors='pt')
        preds = _model.generate(**out, num_beams=1, max_length=50)
        phones = _tokenizer.batch_decode(preds.tolist(), skip_special_tokens=True)
    return ' '.join(phones)


if __name__ == "__main__":
    run(phonemize, "charisiu")
