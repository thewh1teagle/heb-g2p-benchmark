# Heb-G2P Benchmark

See The [Web Page](https://thewh1teagle.github.io/heb-g2p-benchmark) for more details.

Part of [Phonikud project](https://phonikud.github.io)

## Add a new model

1. Create new csv file with `id, phonemes` columns 
2. phonemes should be genereated from the `gt.csv` transcript
3. Run 

```console
uv run src/create_report.py gt.csv pred.csv
```

4. Submit new pull request with the new csv file and the report.json file
