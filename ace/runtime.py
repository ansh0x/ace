import json
from time import perf_counter
from json_repair import repair_json
from .model import LLM
from .searcher import SemanticHotkeyRetriever


class Runtime:
    def __init__(
        self,
        model_path,
        cache_dir,
        no_cache,
        hotkeys_path,
        llm_quant=True,
        cache_size=2,
        verbose=False,
    ):
        self.llm = LLM(
            model_path=model_path,
            quantized=llm_quant,
            no_cache=no_cache,
            cache_dir=cache_dir,
            cache_size=cache_size,
            verbose=verbose,
        )
        self.hotker_retriever = SemanticHotkeyRetriever(
            model_path=model_path,
            hotkeys_path=hotkeys_path,
            hotkeys_cache=cache_dir / "hotkey",
        )

        self.verbose = verbose

    def __call__(self, task, file_path, iteration_context=None) -> dict:

        start = perf_counter()
        hotkeys = self.hotker_retriever.retrieve_hotkeys(task)
        output = self.llm.generate_plan(
            task=task,
            hotkeys=hotkeys,
            directory=file_path if file_path else None,
            iteration_context=iteration_context,
        )
        end = perf_counter()
        if self.verbose:
            print(f"Plan gererated. Took {end - start:0.2f}sec\nRaw un-parsed:")
            print("\n\t", repr(output), "\n")
        parsed_output = self._parse_json(output)
        if parsed_output:
            return parsed_output
        return None

    def _build_input(self, task, hotkeys, dirs=[], iteration_context=None):
        return json.dumps(
            {
                "task": task,
                "directories": dirs,
                "available_hotkeys": hotkeys,
                "iteration_context": iteration_context,
            }
        )

    def _parse_json(self, raw):
        fixed = repair_json(raw)
        try:
            return json.loads(fixed)
        except json.JSONDecodeError as e:
            print("Could not parse generated json.")
            print(e)
            return None
        except Exception as e:
            print("Some unknown error occured!")
            print(e)
            return None
