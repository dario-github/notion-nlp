import json
import logging
import os
import traceback
from pathlib import Path
from typing import Optional

from tabulate import tabulate

from notion_nlp.core.nlp import NotionTextAnalysis
from notion_nlp.parameter.config import (
    NotionParams,
    PathParams,
    ResourceParams,
    TaskParams,
)
from notion_nlp.parameter.error import ConfigError, TaskError
from notion_nlp.parameter.log import config_log
from notion_nlp.parameter.utils import download_webfile, load_config, load_stopwords

PROJECT_ROOT_DIR = Path(__file__).parent.parent.parent.parent
EXEC_DIR = Path.cwd()


def check_resource():
    # 首次无参数运行时，将资源文件和参数模板下载到当前目录
    # 参数模板
    test_config_path = (
        EXEC_DIR
        / PathParams.configs.value
        / os.path.basename(ResourceParams.test_config_file_url())
    )
    if not test_config_path.exists():
        test_config_path.parent.mkdir(exist_ok=True, parents=True)
        download_webfile(ResourceParams.test_config_file_url(), test_config_path.parent)
        logging.info(f"init config success, file path: {test_config_path}")

    # jieba字典
    jieba_dict_path = (
        EXEC_DIR
        / PathParams.jieba.value
        / os.path.basename(ResourceParams.jieba_dict_url())
    )
    if not jieba_dict_path.exists():
        jieba_dict_path.parent.mkdir(exist_ok=True, parents=True)
        download_webfile(ResourceParams.jieba_dict_url(), jieba_dict_path.parent)
        logging.info(f"download jieba dict success, file path: {jieba_dict_path}")


def first_try():
    """首次运行的准备工作"""
    # 下载资源文件
    check_resource()
    # 检查是否存在生产环境和测试环境的配置文件,如果存在生产环境的配置文件，则执行所有任务
    config_path = EXEC_DIR / PathParams.notion_config.value
    test_config_path = EXEC_DIR / PathParams.notion_test_config.value
    run_all_tasks(config_path if config_path.exists() else test_config_path)


def task_info(config_file: str = (EXEC_DIR / PathParams.notion_config.value).as_posix()):
    """查看任务信息

    Args:
        config_file (str, optional): 参数文件地址. Defaults to "notion_nlp/configs/notion.yaml".
    """
    config = load_config(config_file)
    if not config.tasks:
        raise ConfigError("No tasks provided.")
    print(
        tabulate(
            sorted(
                [task.to_table_row()[:-1] for task in config.tasks],
                key=lambda x: (-x[2], x[0]),
            ),
            headers=config.tasks[0].columns[:-1],
            tablefmt="rounded_grid",
        )
    )


def run_task(
    task=None,
    task_json: Optional[str] = None,
    task_name: Optional[str] = None,
    token: Optional[str] = None,
    config_file: str = (EXEC_DIR / PathParams.notion_config.value).as_posix(),
    download_stopwords: bool = False,
    stopfiles_dir: str = (EXEC_DIR / PathParams.stopwords.value).as_posix(),
    stopfiles_postfix: str = "stopwords.txt",
    top_n: int = 5,
    output_dir: str = (EXEC_DIR).as_posix(),
):
    """运行单个任务，任务字典或任务名必须传入一个

    Args:
        task (TaskParams, optional): 任务信息参数类. Defaults to None.
        task_json (str, optional): 任务信息json字符串. Defaults to None.
        task_name (str, optional): 任务名. Defaults to None.
        token (str, optional): 任务token. Defaults to None.
        config_file (str, optional): 参数文件地址. Defaults to "notion_nlp/configs/notion.yaml".
        download_stopwords (bool, optional): 是否下载停用词. Defaults to False.
        stopfiles_dir (str, optional): 停用词文件目录. Defaults to "notion_nlp/stopwords".
        stopfiles_postfix (str, optional): 停用词文件后缀. Defaults to "stopwords.txt".
        top_n (int, optional): 返回top_n的结果. Defaults to 5.
        output_dir (str, optional): 输出目录. Defaults to "notion_nlp/results".

    Raises:
        ConfigError: 检查任务信息字典和任务名是否存在
        TaskError: 检查任务是否存在或禁用
    """
    if top_n < 1:
        raise ValueError("top_n must be a positive integer")
    # 以下的操作都是为了获取两个参数：notion_header和task参数类
    # 如果config文件存在，可以不用提供token，只需task_name或task其中之一即可
    if Path(config_file).exists():
        # task/task_json/task_name 至少提供一个
        if not task and not task_json and not task_name:
            raise ConfigError("Task or Task Name, there must be one.")
        config = load_config(config_file)
        # request的header信息
        notion_header = config.notion.header
        # 如果task/task_json为空，就检查输入的task_name是否存在
        if not task and not task_json:
            # 查找task_name是否存在，如果存在，就检查是否激活中
            if task_name not in config.tasks_map:
                raise TaskError(f"{task_name} does not exist.")
            else:
                task = config.tasks_map[task_name]
            # 检查task是否处于激活中
            if not task.run:
                raise TaskError(
                    f"{task_name} has been set to stop running. Check the parameters."
                )
    # 如果config文件不存在，就必须提供token和task/task_json
    else:
        if not token:
            raise ConfigError("Token is required.")
        notion_header = NotionParams(token).header
    # 至此，notion_header已确定获取
    # task为空，就从task_json构建参数类，至此，完成参数类构建
    if not task:
        try:
            task = json.loads(task_json)
        except json.JSONDecodeError:
            raise ConfigError("Invalid task json.")
        else:
            task = TaskParams(**task)  # 转为参数类
    # 至此，task已确定获取
    # 任务名称及描述
    task_name = task.name
    task_describe = task.describe
    # 需要读取的database ID
    database_id = task.database_id

    # 停用词
    stopwords = load_stopwords(stopfiles_dir, stopfiles_postfix, download_stopwords)

    # 筛选 property，这里的 Label 是上述 database 中的属性
    extra_data = task.extra
    try:
        notion_text_analysis = NotionTextAnalysis(
            notion_header, task_name, task_describe, database_id, extra_data
        )
        notion_text_analysis.run(stopwords, output_dir=output_dir, top_n=top_n)
    except Exception as e:
        # 提取 traceback 信息
        tb = traceback.extract_tb(e.__traceback__)
        # 打印traceback 记录的文件名和行数
        logging.error("".join(traceback.format_list(tb)) + e.__str__())


def run_all_tasks(
    config_file: str = (EXEC_DIR / PathParams.notion_config.value).as_posix(),
):
    """运行所有任务

    Args:
        config_file (str, optional): 参数文件地址. Defaults to "notion_nlp/configs/notion.yaml".
    """
    # 配置日志参数
    config_log(
        EXEC_DIR.stem,
        "run_all_tasks",
        log_root=(EXEC_DIR / "logs").as_posix(),
        print_terminal=True,
        enable_monitor=False,
    )
    # 打印所有任务信息
    task_info(config_file)
    # 获取参数类
    config = load_config(config_file)
    for task in config.tasks:
        if not task.run:
            continue
        run_task(task=task, token=config.notion.token)
