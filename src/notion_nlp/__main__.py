from pathlib import Path

import typer

from notion_nlp.core.task import check_resource
from notion_nlp.core.task import first_try as _first_try
from notion_nlp.core.task import run_all_tasks as _run_all_tasks
from notion_nlp.core.task import run_task as _run_task
from notion_nlp.core.task import task_info as _task_info
from notion_nlp.parameter.config import PathParams
from notion_nlp.parameter.log import config_log

app = typer.Typer()

PROJECT_ROOT_DIR = Path(__file__).parent.parent.parent
EXEC_DIR = Path.cwd()


@app.command()
def first_try():
    _first_try()


@app.command()
def run_all_tasks(
    config_file: str = EXEC_DIR / PathParams.notion_config.value,
):
    _run_all_tasks(config_file)


@app.command()
def run_task(
    task_json: typer.Option[str] = typer.Option(None, help="task infomation json"),
    task_name: typer.Option[str] = typer.Option(None, help="task name"),
    token: typer.Option[str] = typer.Option(None, help="notion Integration token"),
    config_file: typer.Option[str] = typer.Option(None, help="config file path"),
    download_stopwords: typer.Option[bool] = typer.Option(True, help="config file path"),
    stopfiles_dir: typer.Option[str] = typer.Option(
        (EXEC_DIR / PathParams.stopwords.value).as_posix(), help="stopwords files dir"
    ),
    stopfiles_postfix: typer.Option[str] = typer.Option(
        "stopwords.txt", help="stopwords postfix"
    ),
    top_n: typer.Option[int] = typer.Option(5, help="output top n words"),
    output_dir: typer.Option[str] = typer.Option(
        (EXEC_DIR).as_posix(), help="output dir"
    ),
):
    _run_task(
        None,
        task_json,
        task_name,
        token,
        config_file,
        download_stopwords,
        stopfiles_dir,
        stopfiles_postfix,
        top_n,
        output_dir,
    )


@app.command()
def task_info(config_file: str = (EXEC_DIR / PathParams.notion_config.value).as_posix()):
    _task_info(config_file)


if __name__ == "__main__":
    config_log(
        EXEC_DIR.stem,
        "app",
        log_root=(EXEC_DIR / "logs").as_posix(),
        print_terminal=True,
        enable_monitor=False,
    )
    check_resource()
    app()
