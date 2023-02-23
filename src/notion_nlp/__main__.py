from pathlib import Path

import typer

from notion_nlp.core.task import check_resource
from notion_nlp.core.task import first_try as _first_try
from notion_nlp.core.task import run_all_tasks as _run_all_tasks
from notion_nlp.core.task import run_task as _run_task
from notion_nlp.core.task import task_info as _task_info
from notion_nlp.parameter.config import PathParams

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
    task_json: str = typer.Argument(..., help="任务信息json字符串"),
    task_name: str = typer.Argument(..., help="任务名"),
    token: str = typer.Argument(..., help="notion Integration token"),
    config_file: str = (EXEC_DIR / PathParams.notion_config.value).as_posix(),
    download_stopwords: bool = False,
    stopfiles_dir: str = (EXEC_DIR / PathParams.stopwords.value).as_posix(),
    stopfiles_postfix: str = "stopwords.txt",
    top_n: int = 5,
    output_dir: str = (EXEC_DIR).as_posix(),
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
    check_resource()
    app()
