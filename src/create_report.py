import jiwer
import csv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('gt_file', type=str, default='gt.csv')
parser.add_argument('report_file', type=str, default='report.json')
args = parser.parse_args()

with open(args.gt_file, 'r') as f:
    gt_reader = csv.reader(f)
    for row in gt_reader:
        id = row[0]
        transcript = row[1]
        phonemes = row[2]
        print(id, transcript, phonemes)