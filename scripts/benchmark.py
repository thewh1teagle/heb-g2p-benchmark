# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "jiwer",
# ]
# ///

"""
Score all pred TSVs in web/data/ against gt.tsv:
    uv run scripts/benchmark.py

Run a model manually then score:
    uv run src/renikud.py
    uv run src/charisiu.py
    uv run src/dicta.py
    uv run src/espeak_ng.py
    uv run src/gemini31_pro_high_openrouter.py
    uv run src/gemma3.py
    uv run src/goruut.py
    uv run src/nakdimon.py
    uv run src/phonikud_model.py
    uv run src/phonikud_naive.py
"""

import csv
import json
import re
import jiwer
from pathlib import Path

ROOT = Path(__file__).parent.parent
VOWELS = 'aeiou'

MODELS = [
    {"id": "charisiu",                     "name": "Charsiu",                        "description": "Multilingual G2P model based on ByT5 small architecture",                             "url": "https://huggingface.co/charsiu/g2p_multilingual_byT5_small_100"},
    {"id": "dicta",                        "name": "Dicta",                          "description": "Israeli NLP G2P system by the Dicta project",                                         "url": "https://dicta.org.il"},
    {"id": "espeak_ng",                    "name": "ESpeak-NG",                      "description": "Open-source rule-based speech synthesizer with built-in G2P",                         "url": "https://github.com/espeak-ng/espeak-ng"},
    {"id": "gemini31_pro_high",            "name": "Gemini 3.1 Pro (High Thinking)", "description": "Google's Gemini 3.1 Pro LLM with high thinking level via OpenRouter",               "url": "https://deepmind.google/technologies/gemini/"},
    {"id": "gemma3",                       "name": "Gemma3-G2P",                     "description": "Google's Gemma 3 model fine-tuned for G2P conversion",                               "url": "https://github.com/thewh1teagle/gemma3-g2p"},
    {"id": "goruut",                       "name": "Goruut",                         "description": "Rule-based multilingual G2P system written in Go",                                   "url": "https://github.com/neurlang/goruut"},
    {"id": "nakdimon",                     "name": "Nakdimon",                       "description": "Hebrew diacritization model used as a G2P base",                                     "url": "https://github.com/elazarg/nakdimon"},
    {"id": "phonikud",                     "name": "Phonikud",                        "description": "Dedicated Hebrew G2P model based on fine-tuned transformer architecture",           "url": "https://github.com/thewh1teagle/phonikud"},
    {"id": "phonikud_naive",               "name": "Phonikud (Naive)",                "description": "Phonikud model without post-processing, direct diacritization output",               "url": "https://github.com/thewh1teagle/phonikud"},
    {"id": "renikud",                      "name": "Renikud",                        "description": "Hebrew G2P model based on DictaBERT character-level encoder with CTC decoding",      "url": "https://github.com/thewh1teagle/renikud"},
]


def detect_delimiter(path):
    with open(path, encoding='utf-8') as f:
        header = f.readline()
    return '\t' if '\t' in header else ','


def load_tsv(path):
    with open(path, encoding='utf-8') as f:
        first = f.readline()
        has_header = 'Sentence' in first or 'sentence' in first
        f.seek(0)
        if has_header:
            reader = csv.DictReader(f, delimiter='\t')
            return {row['Sentence']: row['Phonemes'] for row in reader}
        else:
            reader = csv.reader(f, delimiter='\t')
            return {row[0]: row[1] for row in reader if len(row) >= 2}


def extract_stress_positions(phonemes):
    words = phonemes.split()
    positions = []
    for word in words:
        for i, char in enumerate(word):
            if char == 'ˈ' and i + 1 < len(word) and word[i + 1] in VOWELS:
                vowel_count = sum(1 for c in word[:i] if c in VOWELS)
                positions.append(str(vowel_count))
                break
        else:
            positions.append('X')
    return ' '.join(positions)


def score(gt: dict, pred: dict):
    wer_scores, cer_scores, stress_scores = [], [], []
    for sentence, gt_ph in gt.items():
        pred_ph = pred.get(sentence)
        if pred_ph is None:
            continue
        wer_scores.append(jiwer.wer(gt_ph, pred_ph))
        cer_scores.append(jiwer.cer(gt_ph, pred_ph))
        stress_scores.append(jiwer.wer(extract_stress_positions(gt_ph), extract_stress_positions(pred_ph)))
    n = len(wer_scores)
    if n == 0:
        return None
    return {
        'wer': sum(wer_scores) / n,
        'cer': sum(cer_scores) / n,
        'stress_wer': sum(stress_scores) / n,
        'n': n,
        'wers': wer_scores,
        'cers': cer_scores,
    }


def run():
    data_dir = ROOT / "web" / "data"
    gt = load_tsv(data_dir / "gt.tsv")
    pred_files = sorted(p for p in data_dir.glob("*.tsv") if p.name != "gt.tsv")
    if not pred_files:
        print("No pred TSVs found in web/data/")
        return

    model_by_id = {m["id"]: m for m in MODELS}
    scored_models = []

    print(f"\n{'Model':<35} {'WER':>6} {'CER':>6} {'StressWER':>10} {'N':>5}")
    print(f"{'-'*35} {'-'*6} {'-'*6} {'-'*10} {'-'*5}")

    for path in pred_files:
        model_id = path.stem
        result = score(gt, load_tsv(path))
        if result is None:
            print(f"{model_id:<35} {'NO MATCH':>6}")
            continue
        print(f"{model_id:<35} {result['wer']:>6.4f} {result['cer']:>6.4f} {result['stress_wer']:>10.4f} {result['n']:>5}")
        meta = model_by_id.get(model_id, {"id": model_id, "name": model_id, "description": "", "url": ""})
        scored_models.append({
            "id": meta["id"],
            "name": meta["name"],
            "description": meta["description"],
            "url": meta["url"],
            "wer": round(result["wer"], 4),
            "cer": round(result["cer"], 4),
            "stress_wer": round(result["stress_wer"], 4),
            "n": result["n"],
            "wers": [round(x, 4) for x in result["wers"]],
            "cers": [round(x, 4) for x in result["cers"]],
        })

    metadata_json = ROOT / "web" / "data" / "metadata.json"
    existing = json.loads(metadata_json.read_text(encoding="utf-8")) if metadata_json.exists() else {}
    output = {
        "title": existing.get("title", "Hebrew G2P Benchmark"),
        "description": existing.get("description", ""),
        "models": scored_models,
    }
    # Serialize with indent but keep wers/cers arrays on one line
    for model in output["models"]:
        model["wers"] = "__WERS__" + json.dumps(model["wers"], ensure_ascii=False) + "__END__"
        model["cers"] = "__CERS__" + json.dumps(model["cers"], ensure_ascii=False) + "__END__"
    text = json.dumps(output, indent=2, ensure_ascii=False)
    text = re.sub(r'"__(WERS|CERS)__(.*?)__END__"', lambda m: m.group(2), text, flags=re.DOTALL)
    metadata_json.write_text(text + "\n", encoding="utf-8")
    print(f"\nWrote {metadata_json}")


run()
