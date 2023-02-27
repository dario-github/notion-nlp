import logging
import shutil
import ssl
import sys
from functools import reduce
from glob import glob
from pathlib import Path
from typing import List
from unicodedata import category

from notion_nlp.parameter.config import (
    APIParams,
    ConfigParams,
    NLPParams,
    NotionParams,
    ResourceParams,
    TaskParams,
    TextCleanParams,
    VisualParams,
)


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
    params = ResourceParams
    if not bool(stopfiles):
        # 下载 `params.multilingual_stopwords_url` 中指定的多语言停用词文件，并解压到 `stopfiles_dir` 目录下
        unzip_webfile(params.multilingual_stopwords_url.value, stopfiles_dir)
        stopfiles = load_local_files(stopfiles_dir, stopfiles_postfix)

    # 如果已经有文件，但仍需要下载停用词，检查是否已下载过，如果未下载过，则添加自定义的停用词
    elif download_stopwords:
        # 检查下载记录文件，获取已下载的文件列表
        with open(Path(stopfiles_dir) / ".DOWNLOAD_RECORDS", "r", encoding="utf-8") as f:
            downloaded_files = set([line.strip() for line in f])
        if params.multilingual_stopwords_url.value not in downloaded_files:
            # 下载 `params.multilingual_stopwords_url` 中指定的多语言停用词文件，并解压到 `stopfiles_dir` 目录下
            unzip_webfile(params.multilingual_stopwords_url.value, stopfiles_dir)
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


def dict_to_class(data, last_key: str = "config"):
    class_map = dict(
        config=ConfigParams,
        tasks=TaskParams,
        visual=VisualParams,
        nlp=NLPParams,
        textclean=TextCleanParams,
        api=APIParams,
        notion=NotionParams,
    )
    if last_key not in class_map.keys():
        return data
    if isinstance(data, dict):
        return class_map.get(last_key, ConfigParams)(
            **{k: dict_to_class(v, k) for k, v in data.items()}
        )
    elif isinstance(data, list):
        return [dict_to_class(v, last_key) for v in data]
    else:
        return data


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
        data = yaml.load(f)
    config = dict_to_class(data)
    # todo 检查config中的结构和参数是否有错误，匹配为正确的参数类，填充缺失值为对应默认值
    # config = origin_config.check_and_fill_missing_params(origin_config)
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
    file_path = Path(target_dir) / os.path.basename(url)
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)  # 创建一个SSLContext对象，指定TLSv1.2协议
    with urllib.request.urlopen(
        url, context=context
    ) as response:  # 打开一个URL，传入SSLContext对象
        with open(file_path, "wb") as file:  # 打开一个文件对象，传入'wb'模式
            shutil.copyfileobj(response, file)  # 将URL的内容复制到文件对象
    logging.info(f"Downloaded {file_path}")
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
