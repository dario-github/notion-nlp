import logging


def load_stopwords(stopfiles):
    import sys
    from functools import reduce
    from glob import glob
    from unicodedata import category
    from urllib.parse import urlencode

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


def load_config(config_file: str = "configs/config.yaml"):
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
    return config
