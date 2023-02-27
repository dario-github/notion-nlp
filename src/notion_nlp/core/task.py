import json
import logging
import os
import traceback
from pathlib import Path
from typing import List, Optional, Tuple

from tabulate import tabulate
from tqdm import tqdm

from notion_nlp.core.nlp import NotionTextAnalysis
from notion_nlp.parameter.config import (
    NotionParams,
    PathParams,
    ResourceParams,
    TaskParams,
)
from notion_nlp.parameter.error import ConfigError, TaskError
from notion_nlp.parameter.utils import (
    dict_to_class,
    download_webfile,
    load_config,
    load_stopwords,
)

PROJECT_ROOT_DIR = Path(__file__).parent.parent.parent.parent
EXEC_DIR = Path.cwd()


def check_resource():
    # 首次无参数运行时，将资源文件和参数模板下载到当前目录
    # 参数模板
    test_config_path = (
        EXEC_DIR
        / PathParams.configs.value
        / os.path.basename(ResourceParams.test_config_file_url.value)
    )
    if not test_config_path.exists():
        test_config_path.parent.mkdir(exist_ok=True, parents=True)
        logging.info(
            f"Downloading test config file from {ResourceParams.test_config_file_url.value}"
        )
        download_webfile(
            ResourceParams.test_config_file_url.value, test_config_path.parent.as_posix()
        )
        logging.info(f"init config success, file path: {test_config_path}")

    # jieba字典
    jieba_dict_path = (
        EXEC_DIR
        / PathParams.jieba.value
        / os.path.basename(ResourceParams.jieba_dict_url.value)
    )
    if not jieba_dict_path.exists():
        jieba_dict_path.parent.mkdir(exist_ok=True, parents=True)
        logging.info(f"Downloading jieba dict from {ResourceParams.jieba_dict_url.value}")
        download_webfile(
            ResourceParams.jieba_dict_url.value, jieba_dict_path.parent.as_posix()
        )


def first_try():
    """首次运行的准备工作"""
    # 下载资源文件
    logging.info(f"Project Dir: {PROJECT_ROOT_DIR.absolute()}")
    logging.info(f"Exec Dir: {EXEC_DIR.absolute()}")
    check_resource()
    # 检查是否存在生产环境和测试环境的配置文件,如果存在生产环境的配置文件，则执行所有任务
    config_path = EXEC_DIR / PathParams.notion_config.value
    test_config_path = EXEC_DIR / PathParams.notion_test_config.value
    run_all_tasks(
        config_path.as_posix() if config_path.exists() else test_config_path.as_posix()
    )


def task_info(
    config_file: str = (EXEC_DIR / PathParams.notion_config.value).as_posix(),
    sort_by: List[Tuple[str, bool]] = [("run", True), ("name", False)],
    exclude: List[str] = ["visual", "nlp", "api"],
):
    """查看任务信息

    Args:
        config_file (str, optional): 参数文件地址. Defaults to "notion_nlp/configs/config.yaml".
    """
    config = load_config(config_file)
    if not config.tasks_with_diff_name():
        raise ConfigError("No tasks provided.")
    table_header, table_row = config.to_sorted_table_row(keys=sort_by, exclude=exclude)
    print("\n", "-" * 10, "|  All Tasks Info  |", "-" * 10, "\n")
    print(
        tabulate(
            table_row,
            headers=table_header,
            tablefmt="rounded_grid",
        )
    )
    print("\n")


def run_task(
    task=None,
    task_json: Optional[str] = None,
    task_name: Optional[str] = None,
    config_file: str = (EXEC_DIR / PathParams.notion_config.value).as_posix(),
    download_stopwords: bool = True,
    stopfiles_dir: str = (EXEC_DIR / PathParams.stopwords.value).as_posix(),
    stopfiles_postfix: str = "stopwords.txt",
    output_dir: str = (EXEC_DIR).as_posix(),
):
    """运行单个任务，任务字典或任务名必须传入一个

    Args:
        task (TaskParams, optional): 任务信息参数类. Defaults to None.
        task_json (str, optional): 任务信息json字符串. Defaults to None.
        task_name (str, optional): 任务名. Defaults to None.
        config_file (str, optional): 参数文件地址. Defaults to "notion_nlp/configs/config.yaml".
        download_stopwords (bool, optional): 是否下载停用词. Defaults to False.
        stopfiles_dir (str, optional): 停用词文件目录. Defaults to "notion_nlp/stopwords".
        stopfiles_postfix (str, optional): 停用词文件后缀. Defaults to "stopwords.txt".

    Raises:
        ConfigError: 检查任务信息字典和任务名是否存在
        TaskError: 检查任务是否存在或禁用
    """
    # 以下的操作都是为了获取task参数类
    # 如果config文件存在，只需task_name或task其中之一即可
    if Path(config_file).exists():
        # task/task_json/task_name 至少提供一个
        if not task and not task_json and not task_name:
            raise ConfigError("Task or Task Name, there must be one.")
        config = load_config(config_file)

        # 如果task/task_json为空，就检查输入的task_name是否存在
        if not task and not task_json:
            # 查找task_name是否存在，如果存在，就检查是否激活中
            task = config.get_task_by_name(task_name)
            if not task:
                raise TaskError(f"{task_name} does not exist.")
                return
            # 检查task是否处于激活中
            if not task.run:
                raise TaskError(
                    f"{task_name} has been set to stop running. Check the parameters."
                )
                return

    # 如果config文件不存在，就必须提供task/task_json
    else:
        if not task and not task_json:
            raise ConfigError("Task or Task Json, there must be one.")
        # task为空，就从task_json构建参数类，至此，完成参数类构建
        elif not task:
            try:
                task_dict = json.loads(task_json)
            except json.JSONDecodeError:
                raise ConfigError("Invalid task json.")
            else:
                task = dict_to_class(task_dict, "tasks")  # 转为参数类
        # 至此，task已确定获取
    assert isinstance(task, TaskParams), "task must be TaskParams."

    # 停用词
    stopwords = load_stopwords(stopfiles_dir, stopfiles_postfix, download_stopwords)

    # 筛选 property，这里的 Label 是上述 database 中的属性
    try:
        notion_text_analysis = NotionTextAnalysis(task)
        notion_text_analysis.run(
            stopwords=stopwords,
            output_dir=output_dir,
        )
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
        config_file (str, optional): 参数文件地址. Defaults to "notion_nlp/configs/config.yaml".
    """
    # 打印所有任务信息
    task_info(config_file)
    # 获取参数类
    config = load_config(config_file)
    tasks_to_run = [task for task in config.tasks_with_diff_name() if task.run]
    logging.info(
        f"Running {len(tasks_to_run)} tasks: {[task.name for task in tasks_to_run]}"
    )
    for task in tqdm(tasks_to_run, desc="Total Tasks"):
        run_task(task=task, config_file=config_file)


if __name__ == "__main__":
    # 获取参数类
    run_all_tasks(config_file=EXEC_DIR / PathParams.notion_test_config.value)
