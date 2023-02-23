import logging
import sys
from functools import reduce
from glob import glob
from pathlib import Path
from typing import List
from unicodedata import category

from notion_nlp.parameter.config import CleanTextParams, ConfigParams, TaskParams


def load_stopwords(stopfiles_dir: str, stopfiles_postfix: str, download_stopwords: bool):
    """加载停用词

    Args:
        stopfiles (_type_): _description_

    Returns:
        _type_: _description_
    """

    # 定义函数 `load_local_files`，用于查找指定目录下的所有符合条件的文件
    def load_local_files(stopfiles_dir: str, stopfiles_postfix: str) -> List[str]:
        return glob((Path(stopfiles_dir) / f"*{stopfiles_postfix}").absolute().as_posix())

    # 查找所有的标点符号
    codepoints = range(sys.maxunicode + 1)
    punctuation = {c for k in codepoints if category(c := chr(k)).startswith("P")}

    # 加载所有的停用词文件
    stopfiles = load_local_files(stopfiles_dir, stopfiles_postfix)

    # 如果缺失停用词文件，下载
    params = CleanTextParams()
    if not bool(stopfiles):
        # 下载 `params.multilingual_stopwords_url` 中指定的多语言停用词文件，并解压到 `stopfiles_dir` 目录下
        unzip_webfile(params.multilingual_stopwords_url(), stopfiles_dir)
        stopfiles = load_local_files(stopfiles_dir, stopfiles_postfix)

    # 如果已经有文件，但仍需要下载停用词，检查是否已下载过，如果未下载过，则添加自定义的停用词
    elif download_stopwords:
        # 检查下载记录文件，获取已下载的文件列表
        with open(Path(stopfiles_dir) / ".DOWNLOAD_RECORDS", "r", encoding="utf-8") as f:
            downloaded_files = set([line.strip() for line in f])
        if params.multilingual_stopwords_url not in downloaded_files:
            # 下载 `params.multilingual_stopwords_url` 中指定的多语言停用词文件，并解压到 `stopfiles_dir` 目录下
            unzip_webfile(params.multilingual_stopwords_url, stopfiles_dir)
            stopfiles = load_local_files(stopfiles_dir, stopfiles_postfix)

    if not bool(stopfiles):
        # 如果没有找到任何停用词文件，则只返回标点符号
        logging.error("No stopfiles provided.")
        return punctuation

    # 加载所有的停用词文件，将其中所有的词都转换为小写，然后取并集
    stopwords = reduce(
        lambda x, y: x.union(y),
        [
            set(
                [x.strip().lower() for x in open(file, "r", encoding="utf-8").readlines()]
            )
            for file in stopfiles
        ],
    )
    # 打印出停用词的个数
    logging.info(f"Loaded {len(stopfiles)} stopwords files.")
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

    # # define custom tag handler
    # def join(loader, node):
    #     seq = loader.construct_sequence(node)
    #     return "".join([str(i) for i in seq])

    # # register the tag handler
    # yaml.constructor.add_constructor("!join", join)

    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.load(f)
    tasks = [TaskParams(**task) for task in config["tasks"]]
    config = ConfigParams(config["notion"]["token"], tasks)
    return config


def download_webfile(url: str, target_dir: str):
    """下载 `url` 中的文件到 `target_dir` 目录下

    Args:
        url (str): 下载地址.
        target_dir (str): 下载目录.
    """
    import os
    import urllib.request

    # 下载 `url` 中的文件到 `target_dir` 目录下
    urllib.request.urlretrieve(url, Path(target_dir) / os.path.basename(url))
    logging.info(f"Downloaded {url} to {target_dir}.")
    # 在目标目录记录下载过的网址，避免重复下载
    with open(Path(target_dir) / ".DOWNLOAD_RECORDS", "a", encoding="utf-8") as f:
        f.write(url + "\n")


def unzip_webfile(url: str, target_dir: str):
    import io
    import urllib.request
    import zipfile

    with urllib.request.urlopen(url) as response:
        with io.BytesIO(response.read()) as zipfile_bytes:
            # 将 Zip 文件解压到指定目录
            with zipfile.ZipFile(zipfile_bytes) as my_zipfile:
                my_zipfile.extractall(target_dir)
    logging.info(f"Downloaded {url} to {target_dir}")
    # 在目标目录记录下载过的网址，避免重复下载
    with open(Path(target_dir) / ".DOWNLOAD_RECORDS", "a", encoding="utf-8") as f:
        f.write(url + "\n")
