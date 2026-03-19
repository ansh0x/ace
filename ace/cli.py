import click
from .config import HOME, ASCII_LOGO


@click.group(invoke_without_command=True)
@click.version_option()
@click.pass_context
def cli(ctx):

    # If a subcommand was invoked, do nothing here.
    if ctx.invoked_subcommand is None:
        click.echo(ASCII_LOGO)
        click.echo("Welcome to ACE.")
        click.echo("Run: ace [OPTIONS] [TASK] [FILEPATH]")


@cli.command()
@click.argument("task", required=True)
@click.argument("file_path", required=False)
@click.option("-q", "--quantized", is_flag=True, help="Use Q4 quantized model")
@click.option("--no-cache", default=False, is_flag=True, help="Turn off KV cache")
@click.option(
    "--verbose", is_flag=True, help="Print extra statements about the progress"
)
def run(task, file_path, quantized, no_cache, verbose):
    from .executor import Executor

    click.echo("Running...")
    if task:
        click.echo(HOME)
        # print(output)
        executor = Executor(
            task=task,
            quantized=quantized,
            file_path=file_path,
            verbose=verbose,
            no_cache=no_cache,
        )
        executor()
        # print(output) return


@cli.group(invoke_without_command=True)
@click.pass_context
def hotkey(ctx):
    if ctx.invoked_subcommand is None:
        click.echo("Hotkeys")
        click.echo('Run "ace hotkey add <hotkey_name>" to add new key')
        click.echo('run "ace hotkey list" to list available hotkeys with descriptions.')


@hotkey.command()
@click.argument("keyname", required=True)
def add(keyname):
    pass


@hotkey.command("list")
@click.option(
    "-g", "--group", is_flag=True, help="Print the available hotkeys group names."
)
def _list(group):
    from textwrap import wrap
    from shutil import get_terminal_size
    from ._utils import _flatten_hotkeys

    hotkey_list = _flatten_hotkeys()
    if not group:
        key_width = max(len(k) for k in hotkey_list) + 2
        term_width = get_terminal_size().columns
        desc_width = term_width - key_width - 3
        click.echo(f"Key{'':<{key_width - 2}}- Description")
        for key, value in hotkey_list.items():
            desc = value["description"]
            wrapped = wrap(desc, width=desc_width)
            click.echo(f"{key:<{key_width}} - {wrapped[0]}")
            for line in wrapped[1:]:
                click.echo(f"{'':<{key_width}}   {line}")
    else:
        click.echo("Group name:")
        group = set([k.split("-")[0] for k in hotkey_list.keys()])
        for k in group:
            click.echo(k.split("-")[0])


@cli.command()
def init():
    from .setup import setup

    setup()


if __name__ == "__main__":
    cli()
