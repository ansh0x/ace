from time import perf_counter
import os
import pickle
import numpy as np
from .model import Embedder
from ._utils import _flatten_hotkeys, _read_file


class SemanticHotkeyRetriever:
    def __init__(self, model_path, hotkeys_path, hotkeys_cache):
        self.hotkey_db_path = str(hotkeys_path)
        self.cache_dir = str(hotkeys_cache / "hotkey_embeddings.npz")
        self.model_path = os.path.join(model_path, "embedding_model")
        self.model = None  # Lazy load

        # Load hotkey database
        self.hotkey_db = _read_file(self.hotkey_db_path)

        # Try to load cached embeddings
        if self._cache_is_valid():
            self._load_cached_embeddings()
        else:
            self._build_and_cache_embeddings()

    def _cache_is_valid(self):
        """Check if cache exists and is up to date"""
        if not os.path.exists(self.cache_dir):
            return False

        cache_mtime = os.path.getmtime(self.cache_dir)
        db_mtime = os.path.getmtime(self.hotkey_db_path)

        return cache_mtime > db_mtime

    def _load_cached_embeddings(self):
        """Load pre-computed embeddings from disk"""
        data = np.load(self.cache_dir, allow_pickle=True)
        self.embeddings = data["embeddings"].item()
        self.hotkey_names = data["hotkey_names"].tolist()
        print(f"✓ Loaded {len(self.hotkey_names)} cached hotkey embeddings")

    def _build_and_cache_embeddings(self):
        """Compute embeddings and save to cache"""

        print("Building hotkey embeddings...")
        start = perf_counter()

        # Load model (only when needed)
        if self.model is None:
            self.model = Embedder(self.model_path)

        # Flatten nested structure
        flat_hotkeys = _flatten_hotkeys(self.hotkey_db)

        # Compute embeddings
        self.embeddings = {}
        self.hotkey_names = []

        for full_name, hotkey_data in flat_hotkeys.items():
            desc = hotkey_data["description"]
            emb = self.model.encode(desc)
            self.embeddings[full_name] = emb
            self.hotkey_names.append(full_name)

        # Save to cache
        np.savez(
            self.cache_dir,
            embeddings=self.embeddings,
            hotkey_names=np.array(self.hotkey_names),
        )
        end = perf_counter()
        print(
            f"✓ Cached {len(self.hotkey_names)} embeddings to {self.cache_dir}. Took {end - start}secs"
        )

    def _get_dependencies(self, key):
        group, action = key.split("-", 1)

        deps = self.hotkey_db[group][action]["key_need"]

        return deps

    def retrieve_hotkeys(self, instruction, top_k=5, threshold=0.25):
        """Get relevant hotkeys for instruction"""
        # Load model only when querying (lazy)
        if self.model is None:
            self.model = Embedder(self.model_path)

        # Embed query
        query_emb = self.model.encode(instruction)

        # Compute similarities
        scores = {}
        for key_name, key_emb in self.embeddings.items():
            sim = np.dot(query_emb, key_emb) / (
                np.linalg.norm(query_emb) * np.linalg.norm(key_emb)
            )
            scores[key_name] = sim

        # Filter and sort
        initial_result = [
            key_name for key_name, score in scores.items() if score > threshold
        ]
        initial_result = sorted(initial_result, key=lambda k: scores[k], reverse=True)[
            :top_k
        ]

        all_hotkeys = set(initial_result)

        for hotkey in initial_result:
            deps = self._get_dependencies(hotkey)
            all_hotkeys.update(deps)

        results = [hotkey for hotkey in initial_result]

        for hotkey in all_hotkeys:
            if hotkey not in results:
                results.append(hotkey)

        return results

    def get_hotkey_info(self, hotkey_name):
        """
        Get full info for a hotkey

        Input: "general-close_window"
        Output: {"key": "mod+w", "description": "...", "category": "general", "action": "close_window"}
        """
        category, action = hotkey_name.split("-", 1)

        if category in self.hotkey_db and action in self.hotkey_db[category]:
            data = self.hotkey_db[category][action]
            return {
                "key": data.get("key", ""),
                "description": data.get("desctiption") or data.get("description", ""),
                "category": category,
                "action": action,
            }

        return None

    def rebuild_cache(self):
        """Force rebuild of cache (useful for debugging)"""
        self._build_and_cache_embeddings()


class SemanticPathsRetriever:
    """
    Retrieves file paths infered from the given task.
    !!! Currently not being used. Need some refinment to retreive paths accurately.
    """

    def __init__(self, filepath_dir):
        self.filepaths_dir = filepath_dir

    def _fuzzy_find(self, query, threshold=70):
        """
        finds files and directories within the specified directory.

        Args:
            query (str): The search query string.
            directory_path (str): The root directory to start the search from.
            threshold (int): The minimum similarity score (0-100) for a match.

        Returns:
            list: A list of full paths that match the query.
        """
        from rapidfuzz import fuzz

        matches = []

        # Use os.walk to recursively traverse the directory tree
        if not os.path.exists(self.filepaths_dir):
            _build_file_cache()

        with open(str(self.filepaths_dir), "rb") as file:
            file_cache = pickle.load(file)

        for p in file_cache:
            score = fuzz.token_sort_ratio(query, p)
            if score >= threshold:
                matches.append((p, score))

        # Sort matches by score in descending order
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches

    def _build_file_cache(self):
        all_paths = []
        for root, dirs, files in os.walk("."):  # Use '.' for current dir
            for d in dirs:
                full_path = os.path.join(root, d)
                all_paths.append(full_path)
            # Check files
            for f in files:
                full_path = os.path.join(root, f)
                all_paths.append(full_path)

        with open(self.filepaths_dir, "wb") as file:
            pickle.dump(all_path, file)
