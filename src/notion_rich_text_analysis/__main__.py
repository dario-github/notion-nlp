
import logging
from glob import glob
from pathlib import Path
from tabulate import tabulate

from utils import (load_config, load_stopwords)
from notion_rich_text_analysis.notion_db_text import NotionDBText
from notion_rich_text_analysis.notion_text_analysis import NotionTextAnalysis

import typer
app = typer.Typer()


@app.command()
def task_info(config_file: str = "config.yaml"):
    config = load_config(config_file)
    task_info_without_extra = [
        {k: v for k, v in task.items() if k != "extra"} for task in [config['task']]]
    print(tabulate(task_info_without_extra, headers='keys',
          tablefmt='orgtbl', numalign="right", stralign="center"))


@app.command()
def run_task(task: dict = dict(), task_name: str = "",
             config_file: str = "config.yaml",
             stopfiles_dir: str = "./stopwords", stopfiles_postfix: str = "stopwords.txt"):
    # task和task_name必须提供一个
    if not task and not task_name:
        raise KeyError("Task or Task Name, there must be one.")
    config = load_config(config_file)
    # request的header信息
    notion_header = config['notion']['header']
    if not task:
        # 查找任务
        for task in config["task"]:
            if task["name"] == task_name:
                break
        if not task:
            raise ValueError(f"{task_name} does not exist.")
        if not task['run']:
            raise ValueError(
                f"{task_name} has been set to stop running. Check the parameters file.")
    # 任务名称及描述
    task_name = task['name']
    task_describe = task['describe']
    # 需要读取的database ID
    database_id = task['database_id']

    # 停用词
    stopfiles = glob(
        (Path(stopfiles_dir) / f"*{stopfiles_postfix}").absolute().as_posix())
    stopwords = load_stopwords(stopfiles)

    # 筛选 property，这里的 Label 是上述 database 中的属性
    extra_data = task['extra']
    try:
        notion_text_analysis = NotionTextAnalysis(
            notion_header, task_name, task_describe, database_id, extra_data)
        notion_text_analysis.run(
            stopwords, output_dir=Path('./results'), top_n=10)
    except Exception as e:
        logging.error(f'{task_name} failed. \n{e}')


@app.command()
def run_all_task(config_file: str = "config.yaml"):
    config = load_config(config_file)
    # request的header信息
    notion_header = config['notion']['header']
    for task in config['task']:
        run_task(task=task, task_name="")


if __name__ == "__main__":
    app()
