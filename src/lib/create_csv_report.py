"""
Combine ground-truth and multiple prediction TSVs into a single CSV.

Usage:
uv run src/create_csv_report.py gt.tsv combined.csv pred_goruut.tsv pred_phonikud.tsv --names Goruut Phonikud
"""

import argparse
import csv
import os
from typing import Dict, List, Tuple

DELIMITER = '\t'


def load_gt(path: str) -> List[Tuple[str, str, str]]:
    """Load ground-truth preserving file order."""
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=DELIMITER)
        if 'Id' not in reader.fieldnames:
            raise SystemExit("Error: ground-truth file must include an 'Id' column.")
        return [(row['Id'], row['Sentence'], row['Phonemes']) for row in reader]


def load_pred(path: str) -> Dict[str, str]:
    """Load predictions into a lookup dict."""
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=DELIMITER)
        return {row['Sentence']: row['Phonemes'] for row in reader}


def infer_name(path: str) -> str:
    base = os.path.basename(path)
    if base.endswith('.tsv'):
        base = base[:-4]
    if base.startswith('pred_'):
        base = base[5:]
    return base


def main():
    parser = argparse.ArgumentParser(
        description="Merge ground truth and multiple prediction TSVs into one CSV with columns per model."
    )
    parser.add_argument('gt_file', help="Ground-truth TSV (Sentence,Phonemes).")
    parser.add_argument('output', help="Output CSV file.")
    parser.add_argument('pred_files', nargs='+', help="One or more prediction TSV files.")
    parser.add_argument('--names', nargs='+', help="Optional display names matching prediction files.")
    args = parser.parse_args()

    if args.names and len(args.names) != len(args.pred_files):
        raise SystemExit("Error: --names must match the number of prediction files.")

    gt_rows = load_gt(args.gt_file)
    if not gt_rows:
        raise SystemExit("Error: ground-truth file is empty or missing rows.")

    pred_dicts = []
    model_names = []
    for idx, pred_path in enumerate(args.pred_files):
        model_names.append(args.names[idx] if args.names else infer_name(pred_path))
        pred_dicts.append(load_pred(pred_path))

    header = ['id', 'sentence', 'model', 'gt', 'prediction']

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for gt_id, sentence, gt_phonemes in gt_rows:
            for model_name, pred_map in zip(model_names, pred_dicts):
                writer.writerow([
                    gt_id,
                    sentence,
                    model_name,
                    gt_phonemes,
                    pred_map.get(sentence, "")  # empty if missing
                ])

    total_rows = len(gt_rows) * len(model_names)
    print(f"Wrote combined CSV with {total_rows} rows ({len(gt_rows)} sentences x {len(model_names)} models) to {args.output}")


if __name__ == "__main__":
    main()
