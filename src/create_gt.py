"""
wget https://huggingface.co/datasets/thewh1teagle/ILSpeech/resolve/main/speaker2/ilspeech_speaker2_v1.7z
7z x ilspeech_speaker2_v1.7z

uv run src/create_gt.py
"""

import csv
import json

INPUT_DIR = "ilspeech_speaker2_v1"
START_ID = 250
LIMIT = 100

# Load phonemes
with open(f"{INPUT_DIR}/metadata.csv") as f:
    phoneme_data = {row[0]: row[1] for row in csv.reader(f, delimiter='|')}

# Load transcripts
with open(f"{INPUT_DIR}/transcript.json") as f:
    transcripts = json.load(f)

# Write ground truth
with open("gt.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "transcript", "phonemes"])

    selected = 0
    for sid, text in transcripts.items():
        if int(sid) < START_ID:
            continue
        writer.writerow([sid, text, phoneme_data[sid]])
        selected += 1
        if selected >= LIMIT:
            break
