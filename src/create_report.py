"""
uv run src/create_report.py gt.tsv pred.tsv web/reports/report_name.json
"""

import jiwer
import csv
import argparse
import json
import os
from collections import defaultdict

DELIMETER = '\t'

def detect_delimiter(path):
    with open(path, 'r', encoding='utf-8') as f:
        header = f.readline()
    if '\t' in header:
        return '\t'
    return ','

def extract_stress_positions(phonemes):
    """
    Extract stress positions per-word to prevent error cascading.

    Splits by spaces and for each word, finds which vowel (a,e,i,o,u) position
    has the stress mark. Returns position for each word.

    Example: "ʃalˈom ʔolˈam" -> "1 1"
             (word1: a=0, o=1✓ | word2: o=0, a=1✓)
    """
    vowels = 'aeiou'
    words = phonemes.split()
    positions = []

    for word in words:
        # Find stress position within this word
        for i, char in enumerate(word):
            if char == 'ˈ' and i + 1 < len(word) and word[i + 1] in vowels:
                # Count vowels before this stress mark in this word only
                vowel_count = sum(1 for c in word[:i] if c in vowels)
                positions.append(str(vowel_count))
                break  # Only one stress per word
        else:
            # No stress found in this word
            positions.append('X')

    return ' '.join(positions)


parser = argparse.ArgumentParser()
parser.add_argument('gt_file', type=str, default='gt.tsv')
parser.add_argument('pred_file', type=str, default='pred.tsv')
parser.add_argument('output', type=str, default='report.json', help='Output JSON file')
args = parser.parse_args()

def load_rows(path):
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=detect_delimiter(path))
        return [
            {
                'id': row.get('Id'),
                'sentence': row['Sentence'],
                'phonemes': row['Phonemes'],
            }
            for row in reader
        ]


def group_by_sentence(rows):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row['sentence']].append(row['phonemes'])
    return grouped


gt_rows = load_rows(args.gt_file)
pred_rows = load_rows(args.pred_file)
pred_groups = group_by_sentence(pred_rows)
pred_offsets = defaultdict(int)

common_samples = []

for row in gt_rows:
    sentence = row['sentence']
    pred_phonemes_list = pred_groups.get(sentence)
    if not pred_phonemes_list:
        continue

    offset = pred_offsets[sentence]
    if offset >= len(pred_phonemes_list):
        continue

    pred_offsets[sentence] += 1
    common_samples.append({
        'id': row['id'],
        'sentence': sentence,
        'gt_phonemes': row['phonemes'],
        'pred_phonemes': pred_phonemes_list[offset],
    })


def id_sort_key(sample):
    sample_id = sample.get('id')
    if sample_id is None or sample_id == '':
        return None
    try:
        return int(sample_id)
    except ValueError:
        return sample_id


if common_samples and all(id_sort_key(sample) is not None for sample in common_samples):
    common_samples.sort(key=id_sort_key)

if not common_samples:
    print("Error: No common sentences found between ground truth and prediction files")
    exit(1)

print(f"Found {len(common_samples)} common samples")

# Calculate WER, CER, and Stress WER for each sample
individual_results = []
wer_scores = []
cer_scores = []
stress_wer_scores = []

for sample in common_samples:
    sentence = sample['sentence']
    gt_phonemes = sample['gt_phonemes']
    pred_phonemes = sample['pred_phonemes']

    # Calculate WER (Word Error Rate) - treating each phoneme as a "word"
    wer = jiwer.wer(gt_phonemes, pred_phonemes)

    # Calculate CER (Character Error Rate)
    cer = jiwer.cer(gt_phonemes, pred_phonemes)

    # Calculate Stress WER (comparing stress positions)
    gt_stress = extract_stress_positions(gt_phonemes)
    pred_stress = extract_stress_positions(pred_phonemes)
    stress_wer = jiwer.wer(gt_stress, pred_stress)

    wer_scores.append(wer)
    cer_scores.append(cer)
    stress_wer_scores.append(stress_wer)

    individual_results.append({
        'id': sample.get('id'),
        'sentence': sentence,
        'wer': wer,
        'cer': cer,
        'stress_wer': stress_wer,
        'gt_phonemes': gt_phonemes,
        'pred_phonemes': pred_phonemes
    })

# Calculate mean scores
mean_wer = sum(wer_scores) / len(wer_scores) if wer_scores else 0
mean_cer = sum(cer_scores) / len(cer_scores) if cer_scores else 0
mean_stress_wer = sum(stress_wer_scores) / len(stress_wer_scores) if stress_wer_scores else 0

# Create report
report = {
    'summary': {
        'mean_wer': mean_wer,
        'mean_cer': mean_cer,
        'mean_stress_wer': mean_stress_wer,
        'num_samples': len(common_samples)
    },
    'individual': individual_results
}

# Save report to JSON
os.makedirs(os.path.dirname(args.output), exist_ok=True)
with open(args.output, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"\nReport saved to {args.output}")
print("\nSummary:")
print(f"  Mean WER: {mean_wer:.4f}")
print(f"  Mean CER: {mean_cer:.4f}")
print(f"  Mean Stress WER: {mean_stress_wer:.4f}")
print(f"  Samples: {len(common_samples)}")
