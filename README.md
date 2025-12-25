# Heb-G2P Benchmark

See The [Web Page](https://thewh1teagle.github.io/heb-g2p-benchmark) for more details.

Part of [Phonikud project](https://phonikud.github.io)

## Add a new model

1. Create new TSV file with `Sentence, Phonemes` columns
2. phonemes should be generated from the `gt.tsv` sentences
3. Run

```console
uv run src/create_report.py gt.tsv pred.tsv
```

4. Submit new pull request with the new TSV file and the report.json file
