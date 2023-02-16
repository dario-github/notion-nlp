import json
import logging
from glob import glob
from pathlib import Path
from tabulate import tabulate

from notion_rich_text_analysis.parameter.utils import (
    load_config, load_stopwords)
from notion_rich_text_analysis.parameter.log import config_log
from notion_rich_text_analysis.notion_text_analysis import NotionTextAnalysis

import typer
app = typer.Typer()


@app.command()
def task_info(config_file: str = "notion_rich_text_analysis/config.yaml"):
    """查看任务信息

    Args:
        config_file (str, optional): 参数文件地址. Defaults to "notion_rich_text_analysis/config.yaml".
    """
    config = load_config(config_file)
    if not config['task']:
        typer.echo("No task")
        return
    task_info_without_extra = [
        {k: str(v) for k, v in task._items() if k != "extra"} for task in config['task']]
    print(tabulate(task_info_without_extra, headers='keys',
          tablefmt='grid'))


@app.command()
def run_task(task: str = "", task_name: str = "",
             config_file: str = "notion_rich_text_analysis/config.yaml",
             stopfiles_dir: str = "./stopwords", stopfiles_postfix: str = "stopwords.txt"):
    """运行单个任务，任务字典或任务名必须传入一个

    Args:
        task (str, optional): 任务信息字典. Defaults to "".
        task_name (str, optional): 任务名. Defaults to "".
        config_file (str, optional): 参数文件地址. Defaults to "notion_rich_text_analysis/config.yaml".
        stopfiles_dir (str, optional): 停用词文件目录. Defaults to "./stopwords".
        stopfiles_postfix (str, optional): 停用词文件后缀. Defaults to "stopwords.txt".

    Raises:
        KeyError: 检查任务信息字典和任务名是否存在
        ValueError: 检查任务是否存在或禁用
    """
    # task和task_name必须提供一个
    if not task and not task_name:
        raise KeyError("Task or Task Name, there must be one.")
    config = load_config(config_file)
    # request的header信息
    notion_header = {k: str(v) for k, v in config['notion']['header']._items()}
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
    else:
        task = json.loads(task)
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
def run_all_task(config_file: str = "notion_rich_text_analysis/config.yaml"):
    """运行所有任务

    Args:
        config_file (str, optional): 参数文件地址. Defaults to "notion_rich_text_analysis/config.yaml".
    """
    config_log(
        "notion_rich_text_analysis",
        "run_all_task",
        log_root='./logs',
        print_terminal=True,
        enable_monitor=False,
    )
    config = load_config(config_file)

    for task in config['task']:
        run_task(task=json.dumps(task, ensure_ascii=False),
                 task_name="", config_file=config_file)


if __name__ == "__main__":
    app()
