import logging
from typing import List, Optional


class APIParams:
    """用于定义api.py中使用到的参数，作为各种笔记软件API参数类的父类，减少方法冗余"""

    def __init__(self) -> None:
        super().__init__()


class NLPParams:
    """用于定义nlp.py中使用到的参数，作为各种NLP技术参数类的父类，减少方法冗余"""

    def __init__(self) -> None:
        super().__init__()


class NotionParams(APIParams):
    """
    让 header 属性中的值自动更新。
    header 属性被定义为一个属性方法，并且使用 token 属性来生成 header 的值。当你修改 token 属性时，header 属性的值会自动更新。
    """

    def __init__(self, token: Optional[str] = None, api_version: str = "2022-06-28"):
        super().__init__()
        self._token = token
        self.api_version = api_version  # 预留了notion API版本自定义的属性，但考虑到版本不兼容本项目代码的问题，不建议使用
        self._database_id = None
        self._page_id = None

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
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        self._token = value

    @property
    def header(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": self.api_version,
            "Content-Type": "application/json",
        }

    @property
    def database_id(self):
        return self._database_id

    @database_id.setter
    def database_id(self, value):
        self._database_id = value

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


class TaskParams:
    """任务参数类"""

    def __init__(
        self,
        name: str,
        database_id: str,
        run: bool = True,
        describe: str = "task description",
        extra: dict = {},
    ):
        """Task Params
        Args:
            name (str): Custom name for differentiation of output file
            database_id (str): notion database id
            run (bool, optional): run or stop task. Defaults to True.
            describe (str, optional): Description of the current task, used to record what the task is to do. Defaults to 'task description'.
            extra (dict, optional): Extra parameters for the task. Defaults to {}.
        """
        self.columns = ["name", "describe", "run", "database_id", "extra"]
        self.name = name
        self.describe = describe
        self.run = run
        self.database_id = database_id
        self.extra = extra

    def to_table_row(self):
        return [self.name, self.describe, self.run, self.database_id, self.extra]

    def to_dict(self):
        return {
            "name": self.name,
            "describe": self.describe,
            "run": self.run,
            "database_id": self.database_id,
            "extra": self.extra,
        }


class ConfigParams:
    """具有请求request所需所有参数的类"""

    def __init__(self, token, tasks: List[TaskParams]):
        self.notion: APIParams = NotionParams(token)
        self.tasks: List[TaskParams] = self.process_task_name(tasks)
        self.tasks_map: dict = {task.name: task for task in self.tasks}

    @staticmethod
    def process_task_name(tasks: List[TaskParams]):
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


class CleanTextParams(NLPParams):
    """数据清洗参数类"""

    multilingual_stopwords_url: str = "https://github.com/dario-github/notion-nlp/raw/main/resources/stopwords/multilingual_stopwords.zip"


class TextAnalysisParams(NLPParams):
    """文本分析参数类"""

    colormap_types: List = [
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
    font_show: str = "chinese.stzhongs.ttf"
    font_url: str = (
        "https://www.wfonts.com/download/data/2014/06/01/stzhongsong/stzhongsong.zip"
    )
