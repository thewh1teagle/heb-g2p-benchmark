"""
wget https://huggingface.co/thewh1teagle/gemma3-270m-heb-g2p/resolve/main/Modelfile
wget https://huggingface.co/thewh1teagle/gemma3-270m-heb-g2p/resolve/main/model-q8.gguf
ollama create gemma3-270m-heb-g2p -f ./Modelfile

uv pip install ollama tqdm
uv run src/gemma3.py
"""
import ollama
from lib.runner import run
from lib.llm_prompt import SYSTEM_PROMPT


def phonemize(sentence):
    response = ollama.chat(
        model="gemma3-270m-heb-g2p",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": sentence}
        ],
        options={
            "temperature": 0.9,
            "top_p": 0.95,
            "top_k": 64,
            "num_predict": 150,
            "stop": ["<end_of_turn>", "</s>"]
        }
    )
    return response["message"]["content"].strip()


if __name__ == "__main__":
    run(phonemize, "gemma3")
