"""
uv run src/create_report.py gt.tsv pred.tsv reports/report_name.json
"""

import jiwer
import csv
import argparse
import json
import os

parser = argparse.ArgumentParser()
parser.add_argument('gt_file', type=str, default='gt.tsv')
parser.add_argument('pred_file', type=str, default='pred.tsv')
parser.add_argument('output', type=str, default='report.json', help='Output JSON file')
args = parser.parse_args()

# Read ground truth file
gt_data = {}
with open(args.gt_file, 'r', encoding='utf-8') as f:
    gt_reader = csv.DictReader(f, delimiter='\t')
    for row in gt_reader:
        # Use sentence as key since there's no ID column
        sentence = row['Sentence']
        gt_data[sentence] = row['Phonemes']

# Read prediction file
pred_data = {}
with open(args.pred_file, 'r', encoding='utf-8') as f:
    pred_reader = csv.DictReader(f, delimiter='\t')
    for row in pred_reader:
        sentence = row['Sentence']
        pred_data[sentence] = row['Phonemes']

# Find common sentences
common_sentences = set(gt_data.keys()) & set(pred_data.keys())

if not common_sentences:
    print("Error: No common sentences found between ground truth and prediction files")
    exit(1)

print(f"Found {len(common_sentences)} common samples")

# Calculate WER and CER for each sample
individual_results = []
wer_scores = []
cer_scores = []

for sentence in sorted(common_sentences):
    gt_phonemes = gt_data[sentence]
    pred_phonemes = pred_data[sentence]

    # Calculate WER (Word Error Rate) - treating each phoneme as a "word"
    wer = jiwer.wer(gt_phonemes, pred_phonemes)

    # Calculate CER (Character Error Rate)
    cer = jiwer.cer(gt_phonemes, pred_phonemes)

    wer_scores.append(wer)
    cer_scores.append(cer)

    individual_results.append({
        'sentence': sentence,
        'wer': wer,
        'cer': cer,
        'gt_phonemes': gt_phonemes,
        'pred_phonemes': pred_phonemes
    })

# Calculate mean scores
mean_wer = sum(wer_scores) / len(wer_scores) if wer_scores else 0
mean_cer = sum(cer_scores) / len(cer_scores) if cer_scores else 0

# Create report
report = {
    'summary': {
        'mean_wer': mean_wer,
        'mean_cer': mean_cer,
        'num_samples': len(common_sentences)
    },
    'individual': individual_results
}

# Save report to JSON
os.makedirs(os.path.dirname(args.output), exist_ok=True)
with open(args.output, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"\nReport saved to {args.output}")
print(f"\nSummary:")
print(f"  Mean WER: {mean_wer:.4f}")
print(f"  Mean CER: {mean_cer:.4f}")
print(f"  Samples: {len(common_sentences)}")