from huggingface_hub import snapshot_download
from pathlib import Path


def download_model(load_path):
    load_path = Path(load_path)

    embedding_dir = load_path / "embedding_model"
    llm_dir = load_path / "llm"

    sentence_transformer_files = [
        "onnx/model.onnx",
        "config.json",
        "special_tokens_map.json",
        "tokenizer.json",
        "vocab.txt",
    ]

    # Download embedding model. If any of files alreadt exists, skips them
    missing_embedding_files = [
        f for f in sentence_transformer_files if not (embedding_dir / f).exists()
    ]

    if not missing_embedding_files:
        print("✓ Embedding model already complete, skipping.")
    else:
        print(f"Missing embedding files: {missing_embedding_files}")

        snapshot_download(
            repo_id="sentence-transformers/all-minilm-l6-v2",
            allow_patterns=missing_embedding_files,  # download only missing
            local_dir=str(embedding_dir),
        )

    # Check if LLM model directory exists and isn't empty.

    llm_models = ["ace-q4_k_m.gguf", "ace-bf16.gguf"]
    llm_dir = Path(llm_dir)

    # Ensure dir exists before checking
    existing_files = []
    if llm_dir.exists():
        existing_files = [f.name for f in llm_dir.iterdir()]

    missing_llm_models = [f for f in llm_models if f not in existing_files]

    if llm_dir.exists() and not missing_llm_models:
        print("✓ LLM model exists, skipping.")
    else:
        print(f"Downloading missing models: {missing_llm_models or 'all'}")

        snapshot_download(
            repo_id="ansh0x/ace-0.5b-gguf",
            allow_patterns=missing_llm_models if missing_llm_models else llm_models,
            local_dir=str(llm_dir),
        )


if __name__ == "__main__":
    download_model(".ace/models")
