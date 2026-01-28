import csv
from tqdm import tqdm

DELIMETER = ','

def run(phonemize_fn, output_name):
    with open("gt.tsv", "r", encoding="utf-8") as f, \
         open(f"pred_{output_name}.tsv", "w", encoding="utf-8") as f_pred:
        reader = csv.DictReader(f, delimiter=DELIMETER)
        writer = csv.writer(f_pred, delimiter=DELIMETER)
        writer.writerow(["Sentence", "Phonemes"])
        for row in tqdm(reader):
            sentence = row["Sentence"]
            phonemes = phonemize_fn(sentence)
            writer.writerow([sentence, phonemes])
            f_pred.flush()
