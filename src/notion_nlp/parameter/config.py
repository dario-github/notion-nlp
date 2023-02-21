import logging
from typing import List


class NotionParams:
    """
    让 header 属性中的值自动更新。
    header 属性被定义为一个属性方法，并且使用 token 属性来生成 header 的值。当你修改 token 属性时，header 属性的值会自动更新。
    """

    def __init__(self, token: str, api_version: str = "2022-06-28"):
        self._token = token
        self.api_version = api_version  # 预留了notion API版本自定义的属性，但考虑到版本不兼容本项目代码的问题，不建议使用

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


class TaskParams:
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
    def __init__(self, token, tasks: List[TaskParams]):
        self.notion: NotionParams = NotionParams(token)
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
