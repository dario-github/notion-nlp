import logging
import sys
from functools import reduce
from glob import glob
from pathlib import Path

from notion_nlp.parameter.config import ConfigParams, TaskParams


def load_stopwords(stopfiles_dir: str, stopfiles_postfix: str, download_stopwords: bool):
    """加载停用词

    Args:
        stopfiles (_type_): _description_

    Returns:
        _type_: _description_
    """
    from unicodedata import category

    def load_local_files(stopfiles_dir: str, stopfiles_postfix: str):
        return glob((Path(stopfiles_dir) / f"*{stopfiles_postfix}").absolute().as_posix())

    def download_files():
        # todo 添加下载停用词的功能
        pass

    # 标点符号
    codepoints = range(sys.maxunicode + 1)
    punctuation = {c for k in codepoints if category(c := chr(k)).startswith("P")}

    # 停用词
    stopfiles = load_local_files(stopfiles_dir, stopfiles_postfix)
    if download_stopwords and not bool(stopfiles):
        download_files()
        stopfiles = load_local_files(stopfiles_dir, stopfiles_postfix)
    if not stopfiles:
        logging.error("No stopfiles provided.")
        return punctuation
    logging.info(f"Loaded {len(stopfiles)} stopwords files.")
    stopwords = reduce(
        lambda x, y: x.union(y),
        [
            set([x.strip().lower() for x in open(file, "r").readlines()])
            for file in stopfiles
        ],
    )
    logging.info(f"Loaded {len(stopwords)} stopwords.")
    return stopwords | punctuation


def load_config(config_file: str) -> ConfigParams:
    """从配置文件加载参数类

    Args:
        config_file (str): 参数文件地址.

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
