"""
NOTE:
默认参数、文本信息都放在XXXParams里，用 @property 装饰
处理这些信息的通用方法都放在XXXClass里，用 @statemethod 装饰
Param要继承对应的Class，以减少方法冗余
"""

import logging
from enum import Enum
from pathlib import Path
from typing import ClassVar, List, Mapping, Optional, Tuple

PROJECT_ROOT_DIR = Path(__file__).parent.parent.parent.parent


class CommanClass:
    """参数处理时的通用方法"""

    def check_and_fill_missing_params(self, standard_params):
        """检查参数是否有缺失，并填充缺失的参数"""
        return self.create_default_object(self.__dict__, self.__str__, standard_params)

    def create_default_object(
        self, kwargs: Mapping, var_name: str, basis_class: ClassVar
    ):
        """根据给定的 Mapping 键值对，返回一个承载了 kwargs 中 var_name 属性的 basis_class 对象。

        Args:
            default (_type_): _description_
            basis_class (_type_): _description_

        Returns:
            _type_: _description_
        """
        return basis_class(**kwargs.get(var_name, basis_class()).__dict__)


class APIClass(CommanClass):
    """用于定义api.py中使用到的参数，作为各种笔记软件API参数类的父类，减少方法冗余"""

    # todo 待将子类方法抽象出来

    def __init__(self) -> None:
        pass


class NLPClass(CommanClass):
    """用于定义nlp.py中使用到的参数，作为各种NLP技术参数类的父类，减少方法冗余"""

    # todo 待将子类方法抽象出来

    def __init__(self) -> None:
        pass


class VisualClass(CommanClass):
    """用于定义visual.py中使用到的参数，作为各种可视化技术参数类的父类，减少方法冗余"""

    # todo 待将子类方法抽象出来

    def __init__(self) -> None:
        pass


class ConfigPath(str, Enum):
    """各种应用的配置文件路径类"""

    value = Path("configs")
    # todo 支持其他笔记软件的API
    # 用pathlib来自适应不同平台的路径分隔符
    notion = value / "config.yaml"
    notion_test = value / "config.test.yaml"

    def __str__(self):
        return self.value


class ResultPath(str, Enum):
    """各种分析方法的结果存放路径"""

    value = Path("results")

    wordcloud = value / "wordcloud"
    tfidf_analysis = value / "tfidf_analysis"

    def __str__(self):
        return self.value


class ResourcePath(str, Enum):
    """各种应用的资源路径类"""

    value = Path("resources")

    jieba = value / "jieba"
    stopwords = value / "stopwords"
    fonts = value / "fonts"
    backgrouds = value / "backgrouds"

    def __str__(self):
        return self.value


class PathParams(str, Enum):
    """各种文件路径的参数类"""

    value = Path(PROJECT_ROOT_DIR.name + "-dataset")

    configs = value / ConfigPath.value
    results = value / ResultPath.value
    resources = value / ResourcePath.value

    jieba = value / ResourcePath.jieba
    fonts = value / ResourcePath.fonts
    stopwords = value / ResourcePath.stopwords
    backgrouds = value / ResourcePath.backgrouds

    wordcloud = value / ResultPath.wordcloud
    tfidf_analysis = value / ResultPath.tfidf_analysis

    notion_config = value / ConfigPath.notion
    notion_test_config = value / ConfigPath.notion_test

    def __str__(self):
        return self.value


class ResourceParams(str, Enum):
    """资源参数类"""

    # 测试配置文件的url
    test_config_file_url = "https://raw.githubusercontent.com/dario-github/notion-nlp/main/notion-nlp-dataset/configs/config.test.yaml"

    # 字体文件的url
    font_url = (
        "https://www.wfonts.com/download/data/2014/06/01/stzhongsong/stzhongsong.zip"
    )

    # 多语言停用词文件的url
    multilingual_stopwords_url = "https://github.com/dario-github/notion-nlp/raw/main/notion-nlp-dataset/resources/stopwords/multilingual_stopwords.zip"

    # jieba 停用词词典的url
    jieba_dict_url = "https://github.com/fxsjy/jieba/raw/master/jieba/dict.txt"


class TextCleanParams(NLPClass):
    """数据清洗参数类"""

    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.discard_startswith = ["#", "@"]
        self.sentence_length = [9, 999]
        self.__dict__.update(kwargs)

    @property
    def min_sentence_length(self) -> int:
        return self.sentence_length[0]

    @property
    def max_sentence_length(self) -> int:
        return self.sentence_length[1]


class VisualParams(VisualClass):
    def __init__(self, **kwargs):
        self.colormap = "all"  # 私有属性，存储colormap的值
        self.font_show = "chinese.stzhongs.ttf"

        self.__dict__.update(kwargs)

    @staticmethod
    def colormap_types():
        """颜色映射类型 colormap_types不由参数文件配置"""
        return [
            "viridis",
            "plasma",
            "inferno",
            "magma",
            "cividis",
            "cool",
            "coolwarm",
            "YlGn",
            "YlGnBu",
            "RdYlGn",
            "jet",
        ]


class NLPParams(NLPClass):
    def __init__(self, **kwargs):
        super().__init__()
        self.textclean: TextCleanParams = TextCleanParams()
        self.seg_pkg = "jieba"
        self.top_n = 5
        self.__dict__.update(kwargs)


class APIParams(APIClass):
    def __init__(self, **kwargs):
        super().__init__()
        # self._notion = NotionParams()
        # todo 还有其他笔记应用和社交媒体的API
        self.__dict__.update(kwargs)


class TaskParams(CommanClass):
    """文本分析参数类"""

    def __init__(self, **kwargs) -> None:
        super().__init__()
        # self._visual = VisualParams(**kwargs.get("visual", VisualParams()).__dict__)
        self.run: bool = True
        self.description: str = "task description"
        self.visual: VisualParams = VisualParams()
        self.nlp: NLPParams = NLPParams()
        # api必须要有，所以不设置初始值
        self.__dict__.update(kwargs)


class NotionParams(APIClass):
    """
    让 header 属性中的值自动更新。
    header 属性被定义为一个属性方法，并且使用 token 属性来生成 header 的值。当你修改 token 属性时，header 属性的值会自动更新。
    """

    def __init__(self, **kwargs):
        super().__init__()
        self.api_version: str = "2022-06-28"
        self._page_id = None
        self.__dict__.update(kwargs)

    @property
    def block_types(self):
        return [
            "paragraph",
            "bulleted_list_item",
            "numbered_list_item",
            "toggle",
            "to_do",
            "quote",
            "callout",
            "synced_block",
            "template",
            "column",
            "child_page",
            "child_database",
            "table",
            "heading_1",
            "heading_2",
            "heading_3",
        ]

    @property
    def header(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": self.api_version,
            "Content-Type": "application/json",
        }

    @property
    def url_get_pages(self):
        return f"https://api.notion.com/v1/databases/{self.database_id}/query"

    @property
    def page_id(self):
        return self._page_id

    @page_id.setter
    def page_id(self, value):
        self._page_id = value

    @property
    def url_get_blocks(self):
        return f"https://api.notion.com/v1/blocks/{self.page_id}/children"


class ConfigParams(CommanClass):
    """处理参数文件的类"""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def tasks_with_diff_name(self):
        return self.process_task_name(self.tasks)

    @staticmethod
    def process_task_name(tasks):
        # Check whether the task name is the same
        name_cnt_map = dict()
        for k, task in enumerate(tasks):
            if task.name in name_cnt_map:
                name_cnt_map[task.name] += 1
                tasks[k].name += f"_{name_cnt_map[task.name]}"
                logging.warning(f"Task name {task.name} has been used.")
            else:
                name_cnt_map[task.name] = 1
        return tasks

    def to_table_row(self, exclude: List[str] = []):
        table_header = [x for x in self.tasks[0].__dict__.keys() if x not in exclude]
        table_row = [
            [value for key, value in task.__dict__.items() if key not in exclude]
            for task in self.tasks
        ]
        return table_header, table_row

    def to_sorted_table_row(self, keys: List[Tuple[str, bool]], exclude: List[str] = []):
        table_header, table_row = self.to_table_row(exclude)
        key_index = [(table_header.index(key), reverse) for key, reverse in keys]
        sorted_table_row = sorted(
            table_row,
            key=lambda x: [-x[idx] if reverse else x[idx] for idx, reverse in key_index],
        )
        return table_header, sorted_table_row

    def get_task_by_name(self, task_name: str):
        return {task.name: task for task in self.tasks_with_diff_name()}.get(task_name)
