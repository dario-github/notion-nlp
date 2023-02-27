from pathlib import Path
from typing import Optional

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
    task_json: Optional[str] = None,
    task_name: Optional[str] = None,
    config_file: Optional[str] = (EXEC_DIR / PathParams.notion_config.value).as_posix(),
    download_stopwords: Optional[bool] = True,
    stopfiles_dir: Optional[str] = (EXEC_DIR / PathParams.stopwords.value).as_posix(),
    stopfiles_postfix: Optional[str] = "stopwords.txt",
    output_dir: Optional[str] = (EXEC_DIR).as_posix()
):
    """This function is designed to execute a task and produce the results specified in the `task_json` file, which can be specified directly or by referencing a `task_name`.

    `task_json` : Optional[str], optional
        The path to the json file containing the parameters necessary to run the task.
    `task_name` : Optional[str], optional
        The name of the task to execute. If set, it will look for `task_json` in the directory specified by `DEFAULT_TASK_DIR`.
    `token` : Optional[str], optional
        Used to authenticate access to NotionAPI. This is optional if the config file contains valid credentials.
    `config_file`: Optional[str], optional
        Path to configuration file. By default, it uses `EXEC_DIR/PathParams.notion_config.value`.
    `download_stopwords`: Optional[bool], optional
        A boolean flag determining whether the function should search for stopwords. Default set to `True`.
    `stopfiles_dir`: Optional[str], optional
        Path to folder containig stopwords. By default, it uses `EXEC_DIR/PathParams.stopwords.value`.
    `stopfiles_postfix`: Optional[str], optional
        Filename postfix used when downloading stopwords. By default, it uses `"stopwords.txt".`
    `top_n`: Optional[int], optional
        Used to determine which `n` entities are considered most important when computing results.By default, it uses `5`.
    `output_dir`: Optional[str], optional
        The directory where results should be written. By default, it uses `EXEC_DIR`.
    `colormap`: Optional[str], optional
        The colormap used to display results. By default, it uses `"all"`.
    """
    _run_task(
        task=None,
        task_json=task_json,
        task_name=task_name,
        config_file=config_file,
        download_stopwords=download_stopwords,
        stopfiles_dir=stopfiles_dir,
        stopfiles_postfix=stopfiles_postfix,
        output_dir=output_dir,
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
    # check_resource()
    app()
