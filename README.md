# Heb-G2P Benchmark

See the [Web Page](https://thewh1teagle.github.io/heb-g2p-benchmark) for more details.

Part of the [Phonikud project](https://phonikud.github.io)

## Add a new model

1. Create a script in `src/<model_name>.py` that reads from `web/data/gt.tsv` and writes predictions to `web/data/<model_name>.tsv` (two columns: `Sentence`, `Phonemes`, no header)
2. Run your script:
   ```console
   uv run src/<model_name>.py
   ```
3. Score all models and update `web/data/metadata.json`:
   ```console
   uv run scripts/benchmark.py
   ```
4. Submit a pull request with your script, the pred TSV, and the updated `metadata.json`

## Score / leaderboard

```console
uv run scripts/benchmark.py
```
