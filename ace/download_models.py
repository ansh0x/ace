from huggingface_hub import snapshot_download
import os


def download_model(load_path):

    snapshot_download(
        "sentence-transformers/all-MiniLM-L6-v2",
        allow_patterns=[
            "onnx/model.onnx",
            "config.json",
            "special_tokens_map.json",
            "tokenizer.json",
            "tokenizer.json",
            "vocab.txt",
        ],
        local_dir=str(os.path.join(load_path, "embedding_model")),
    )
    snapshot_download(
        repo_id="ansh0x/ace-0.5b-gguf", local_dir=str(os.path.join(load_path, "llm"))
    )


if __name__ == "__main__":
    download_model(".ace/models")
