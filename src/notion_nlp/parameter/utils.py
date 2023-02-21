import logging
from typing import Iterator

from notion_nlp.parameter.config import ConfigParams, TaskParams


def load_stopwords(stopfiles: Iterator):
    """加载停用词

    Args:
        stopfiles (_type_): _description_

    Returns:
        _type_: _description_
    """
    import sys
    from functools import reduce
    from unicodedata import category

    # 标点符号
    codepoints = range(sys.maxunicode + 1)
    punctuation = {c for k in codepoints if category(c := chr(k)).startswith("P")}

    # 停用词
    if not stopfiles:
        logging.error("No stopfiles provided.")
        return punctuation
    stopwords = reduce(
        lambda x, y: x.union(y),
        [set([x.strip() for x in open(file, "r").readlines()]) for file in stopfiles],
    )
    stopwords = stopwords | punctuation
    return stopwords


def load_config(config_file: str = "configs/config.yaml") -> ConfigParams:
    """从配置文件加载参数类

    Args:
        config_file (str, optional): 参数文件地址. Defaults to "configs/config.yaml".

    Returns:
        ConfigParams: 包含所有用于request信息的参数类
    """
    from ruamel.yaml import YAML

    # 使用 yaml 1.2
    yaml = YAML()

    # define custom tag handler
    def join(loader, node):
        seq = loader.construct_sequence(node)
        return "".join([str(i) for i in seq])

    # register the tag handler
    yaml.constructor.add_constructor("!join", join)

    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.load(f)
    tasks = [TaskParams(**task) for task in config["tasks"]]
    config = ConfigParams(config["notion"]["token"], tasks)
    return config


if __name__ == "__main__":
    from pathlib import Path

    from tabulate import tabulate

    PROJECT_ROOT_DIR = Path(__file__).parent.parent.parent.parent

    config = load_config(
        config_file=(PROJECT_ROOT_DIR / "configs/config.test.yaml").as_posix()
    )

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
