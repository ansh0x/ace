import os
import subprocess
import shlex

from ._utils import _read_file
from .runtime import Runtime
from .config import HOME, CONFIG


class Executor:
    def __init__(self, task, file_path, quantized, no_cache, verbose=False) -> None:

        self.task: str = task

        self.file_path = [file_path]

        self.runtime = Runtime(
            HOME / "models",
            cache_dir=HOME / "cache",
            hotkeys_path=HOME / "hotkeys.json",
            llm_quant=quantized,
            no_cache=no_cache,
            verbose=verbose,
            cache_size=CONFIG["llm_cache_size"],
        )

        self.executor: dict = {
            "atomic": self._atomic,
            "repetitive": self._repetitive,
            "clarification": self._clarification,
        }

        self.application: dict = _read_file(str(HOME / "applications.json"))

        self.verbose: bool = verbose

    def _atomic(self, output):
        output = output.get("execution_plan")
        if not output:
            print("Model output is wrong. `execution_plan` not found in the output.")
            redo = input("Do you want to retry?[Y/n]: ")
            if redo.lower() == "y":
                self()
            else:
                print("Aborting!")
                return None
        cli = output["cli"]
        if self.verbose:
            print(cli)
        for commands in cli:
            if isinstance(commands, dict):
                for k, v in commands.items():
                    if k == "exec":
                        self._exec_cli(v)
            elif isinstance(commands, str):
                print("Model output command in an unexpected format.")
                print("Follwing is the commnf:")
                print("\t", commands)
                ok_to_executie = input("Do you want to execute it? [Y/n]: ")
                if ok_to_executie.lower() == "y":
                    return self._exec_cli(commands)

                else:
                    print("Aborting!")
                    return False

    def _repetitive(self, output):
        output = output.get("repetitive_plan")
        if not output:
            print("Model output is wrong. `repetitive_plan` not found in the output.")
            redo = input("Do you want to retry?[Y/n]: ")
            if redo.lower() == "y":
                self()
            else:
                print("Aborting!")
                return None
        file_path = output["file_path"]
        file = _read_file(file_path)
        iteration_var = f"{{{output['iteration_variable']}}}"
        if file:
            init_d = file[0]
        else:
            print("Aborting!")
        task = output["atomic_template"].replace(iteration_var, init_d)
        iteration_context = {
            "current_iteration": 1,
            "iteration_variable": iteration_var,
            "total_iterations": len(file),
        }
        init_plan = self.runtime(task=task, iteration_context=iteration_context)
        print(init_plan)
        return

    def _clarification(self, output):
        print(output["response"])
        return None

    def _exec_cli(self, cmd: str):
        cmd = shlex.split(cmd)
        for i, c in enumerate(cmd):
            if c.startswith("<"):
                if c not in self.application:
                    print(
                        f"<{c}> not defined in {os.path.join(HOME, 'application.json')}. If it is a model's error ignore it, otherwise define it."
                    )
                    return False
                c = c.replace(c, self.application[c])
            if "~" in c:
                c = os.path.expanduser(c)
            cmd[i] = c
        print("Executing:", cmd)
        approve = input("Execute?[Y/n]: ")
        if approve.lower() == "y":
            subprocess.Popen(cmd)
            return True
        else:
            print("Aborted!")
            return False

    def __call__(self) -> None:
        response = self._create_output(self.task, self.file_path)
        if response:
            print("Task type:", self.task_type)
            self.executor[self.task_type](self.output)
        else:
            print("Aborting!!!")

    def _create_output(self, task, file_path=None):
        output = self.runtime(task, file_path)

        if output:
            self.task_type = output["task_type"]
            self.output = output["output"]
            return True
        return False
