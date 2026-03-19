import os
import json
from time import perf_counter
import numpy as np


class LLM:
    def __init__(self, model_path, quantized, no_cache, cache_dir, cache_size, verbose):
        from llama_cpp import Llama
        from llama_cpp.llama_cache import LlamaDiskCache

        self.verbose = verbose

        model_type = f"ace-{'q4_k_m' if quantized else 'bf16'}.gguf"
        print("Loading", model_type, "model...")
        start = perf_counter()
        model_path = os.path.join(model_path, "llm", model_type)
        cache_dir = os.path.join(cache_dir, "llm")
        self.llm = Llama(
            model_path=model_path,
            n_ctx=1024,
            verbose=False,
            flash_attn=False,
        )
        if not no_cache:
            self.cache = LlamaDiskCache(
                cache_dir=cache_dir,
                capacity_bytes=cache_size << 30,  # makes a 2GB cache
            )
            self.llm.set_cache(self.cache)
            if self.verbose:
                print("Initiated KV-cache")
        elif no_cache:
            print("--no-cache has been passed. KV-cache will not be used.")
        end = perf_counter()
        print(f"Model Loaded! Took {end - start:0.2f} s")

    def generate_plan(
        self, task, directory=[], hotkeys=[], iteration_context=None
    ) -> dict:

        inp = f"<prompt>\n{self.input_template(task, directory, hotkeys, iteration_context)}\n<response>"
        if self.verbose:
            print(inp)
        output = self.llm(
            inp,
            max_tokens=256,
            temperature=0.0,
            repeat_penalty=1.1,
        )
        return output["choices"][0]["text"]

    def input_template(self, task, directory, hotkeys, iteration_context):
        return json.dumps(
            {
                "task": task,
                "directory": directory if directory else None,
                "available_hotkeys": hotkeys,
                "iteration_context": iteration_context,
            }
        )


class Embedder:
    def __init__(self, model_path):
        import onnxruntime as ort
        from tokenizers import Tokenizer

        # Load tokenizer
        self.tokenizer = Tokenizer.from_file(os.path.join(model_path, "tokenizer.json"))
        self.tokenizer.enable_truncation(max_length=16)
        self.tokenizer.enable_padding(length=16)

        # Load ONNX model
        self.session = ort.InferenceSession(
            os.path.join(model_path, "onnx", "model.onnx"),
            providers=["CPUExecutionProvider"],
        )

    def _mean_pooling(self, token_embeddings, attention_mask):
        """Mean pooling"""
        input_mask_expanded = np.expand_dims(attention_mask, -1)
        input_mask_expanded = np.broadcast_to(
            input_mask_expanded, token_embeddings.shape
        ).astype(float)

        sum_embeddings = np.sum(token_embeddings * input_mask_expanded, axis=1)
        sum_mask = np.clip(input_mask_expanded.sum(axis=1), a_min=1e-9, a_max=None)

        return sum_embeddings / sum_mask

    def encode(self, text):
        """Encode text to embedding"""
        # Tokenize
        encoded = self.tokenizer.encode(text)
        # Run inference
        outputs = self.session.run(
            None,
            {
                "input_ids": np.asarray([encoded.ids], dtype=np.int64),
                "attention_mask": np.asarray([encoded.attention_mask], dtype=np.int64),
                "token_type_ids": np.asarray([encoded.type_ids], dtype=np.int64),
            },
        )

        # Mean pooling
        embeddings = self._mean_pooling(outputs[0], encoded.attention_mask)

        # Normalize
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

        return embeddings[0]
