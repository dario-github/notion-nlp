from unittest.mock import patch
from pathlib import Path
import pytest
import json

from notion_nlp.parameter.utils import load_config, load_stopwords
from notion_nlp.core.task import run_task, run_all_tasks, check_resource

from notion_nlp.parameter.config import TaskParams, ConfigParams, PathParams, NotionParams
from notion_nlp.parameter.log import config_log
from notion_nlp.parameter.error import NLPError, ConfigError, TaskError
from notion_nlp.core.api import NotionDBText
from notion_nlp.core.nlp import NotionTextAnalysis

PROJECT_ROOT_DIR = Path(__file__).parent.parent
EXEC_DIR = Path.cwd()


@pytest.fixture
def notion_config():
    config_file = PROJECT_ROOT_DIR / PathParams.notion_test_config.value
    config = load_config(config_file)
    return config


@pytest.fixture
def notion_text_analysis(notion_config):
    check_resource()

    task = notion_config.tasks[0]

    header = NotionParams(notion_config.notion.token).header
    task_name = task.name
    task_description = task.description
    database_id = task.database_id
    extra_data = task.extra

    return NotionTextAnalysis(
        header, task_name, task_description, database_id, extra_data
    )


def test_notion_text_analysis_init(notion_text_analysis):
    assert notion_text_analysis.total_texts != []


# def test_notion_text_analysis_run(notion_text_analysis):
#     notion_text_analysis.run(
#         stopwords=set(),
#         output_dir="./results",
#         top_n=5,
#         seg_pkg="jieba",
#     )
#     assert not notion_text_analysis.tf_idf_dataframe.empty


def test_notion_text_analysis_check_stopwords():
    assert NotionTextAnalysis.check_stopwords("the", {"the", "is"}) is True
    assert NotionTextAnalysis.check_stopwords("123", {"the", "is"}) is True
    assert NotionTextAnalysis.check_stopwords("", {"the", "is"}) is True
    assert NotionTextAnalysis.check_stopwords("hello", {"the", "is"}) is False


def test_notion_text_analysis_check_sentence_available():
    assert NotionTextAnalysis.check_sentence_available("#hello world!") is False
    assert NotionTextAnalysis.check_sentence_available("hello world!") is True


def test_notion_text_analysis_split_sentence():
    assert NotionTextAnalysis.split_sentence("今天天气不错，适合出去玩", "jieba") == [
        "今天天气",
        "不错",
        "，",
        "适合",
        "出去玩",
    ]


def test_notion_text_analysis_handling_sentences(notion_text_analysis):
    notion_text_analysis.total_texts = []
    with pytest.raises(NLPError):
        notion_text_analysis.handling_sentences(stopwords=set(), seg_pkg="jieba")
    notion_text_analysis.total_texts = [["今天天气不错，适合出去玩", "#hello"]]
    with pytest.raises(NLPError):
        notion_text_analysis.handling_sentences(
            stopwords={"今天天气", "不错", "，", "适合", "出去玩"}, seg_pkg="jieba"
        )
    notion_text_analysis.total_texts = [["#hello"]]
    with pytest.raises(NLPError):
        notion_text_analysis.handling_sentences(stopwords=set(), seg_pkg="jieba")


# @pytest.mark.usefixtures("notion_config")
class TestNotionDBText:
    @staticmethod
    def setup_class(self):
        config = load_config(PROJECT_ROOT_DIR / PathParams.notion_test_config.value)
        task = config.tasks[0]
        self.database_id = task.database_id
        self.extra_data = task.extra
        self.token = config.notion.token
        self.db_text = NotionDBText(self.token, self.database_id, self.extra_data)

    @patch("requests.post")
    def test_read_pages(self, mock_post):
        mock_post.return_value.text = json.dumps(
            {
                "has_more": False,
                "results": [{"id": "123"}],
                "next_cursor": "abc",
            },
            ensure_ascii=False,
        )
        pages = self.db_text.read_pages()
        assert len(pages) == 1
        assert pages[0]["id"] == "123"

    @patch("requests.get")
    def test_read_blocks(self, mock_get):
        mock_get.return_value.text = json.dumps(
            {"results": [{"id": "456"}]}, ensure_ascii=False
        )
        blocks = self.db_text.read_blocks([{"id": "123"}])
        assert len(blocks) == 1
        assert len(blocks[0]) == 1
        assert blocks[0][0]["id"] == "456"

    def test_read_rich_text(self):
        blocks = [
            [{"type": "paragraph", "paragraph": {"rich_text": [{"plain_text": "test"}]}}]
        ]
        texts = self.db_text.read_rich_text(blocks)
        assert len(texts) == 1
        assert len(texts[0]) == 1
        assert texts[0][0] == "test"


@pytest.fixture
def mock_task():
    # 定义一个mock task用于测试
    return TaskParams(
        name="test", description="testing", database_id="123", extra=[], run=True
    )


def test_run_task_inputs(mock_task):
    # 测试函数输入的参数和异常情况
    with pytest.raises(ConfigError, match="Task or Task Name, there must be one."):
        run_task(
            task=None,
            task_json=None,
            task_name=None,
            config_file=PROJECT_ROOT_DIR / PathParams.notion_test_config.value,
        )

    with pytest.raises(ConfigError, match="Invalid task json."):
        run_task(
            task_json="{invalid json}",
            config_file=PROJECT_ROOT_DIR / PathParams.notion_test_config.value,
        )

    with pytest.raises(TaskError, match="nonexistent does not exist."):
        run_task(
            task_name="nonexistent",
            config_file=PROJECT_ROOT_DIR / PathParams.notion_test_config.value,
        )

    with pytest.raises(
        TaskError,
        match="discarded_task has been set to stop running. Check the parameters.",
    ):
        mock_task.run = False
        run_task(
            task_name="discarded_task",
            config_file=PROJECT_ROOT_DIR / PathParams.notion_test_config.value,
        )

    with pytest.raises(ConfigError, match="Token is required."):
        run_task(task_json="{valid json}", config_file="nonexistent")


def test_run_task_outputs(notion_text_analysis):
    import shutil

    # 测试函数输出的结果类型和内容是否正确
    output_dir = Path("./unittest_results")
    run_task(
        task_name=notion_text_analysis.task_name,
        config_file=PROJECT_ROOT_DIR / PathParams.notion_test_config.value,
        output_dir=output_dir.as_posix(),
    )

    # 测试输出结果是否正确
    # 此处的假设是notion_text_analysis.run()会在output_dir下生成一个文件
    assert (
        output_dir
        / PathParams.tfidf_analysis.value
        / f"{notion_text_analysis.task_name}.top_5.md"
    ).exists()
    # 删除文件
    shutil.rmtree(output_dir)


def test_run_task_subfunctions():
    # 测试函数调用的子函数能否正常调用并返回正确的结果
    config_file = PROJECT_ROOT_DIR / PathParams.notion_test_config.value
    stopfiles_dir = PathParams.stopwords.value
    stopfiles_postfix = "stopwords.txt"

    config = load_config(config_file)
    assert isinstance(config, ConfigParams)

    stopfiles = load_stopwords(stopfiles_dir, stopfiles_postfix, False)
    assert isinstance(stopfiles, set)


def test_run_task_edge_cases(mock_task):
    # 测试函数在一些边界情况下是否能够正常工作
    with pytest.raises(ValueError, match="top_n must be a positive integer"):
        run_task(task=mock_task, top_n=-1)

    with pytest.raises(ValueError, match="top_n must be a positive integer"):
        run_task(task=mock_task, top_n=0)


# def test_run_all_tasks():
#     # 测试从文件运行
#     run_all_tasks(config_file=PROJECT_ROOT_DIR / PathParams.notion_test_config.value)


if __name__ == "__main__":
    config_log(
        EXEC_DIR.stem,
        "unit_test",
        log_root=(EXEC_DIR / "logs").as_posix(),
        print_terminal=True,
        enable_monitor=False,
    )
    pytest.main(["-v", "-s", "-q", "test_notion_nlp.py"])
