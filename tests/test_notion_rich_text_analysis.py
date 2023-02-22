from unittest.mock import patch
from pathlib import Path
from glob import glob
import pytest
import json

from notion_nlp.parameter.utils import load_config, load_stopwords
from notion_nlp import run_task, run_all_tasks

from notion_nlp.parameter.config import TaskParams, ConfigParams
from notion_nlp.parameter.log import config_log
from notion_nlp.parameter.error import NLPError, ConfigError, TaskError
from notion_nlp.core.api import NotionDBText
from notion_nlp.core.nlp import NotionTextAnalysis

PROJECT_ROOT_DIR = Path(__file__).parent.parent

config_file = PROJECT_ROOT_DIR / "configs/config.test.yaml"
CONFIG = load_config(config_file)


@pytest.fixture
def notion_text_analysis():
    header = CONFIG.notion.header
    task_name = CONFIG.tasks[0].name
    task_describe = CONFIG.tasks[0].describe
    database_id = CONFIG.tasks[0].database_id
    extra_data = CONFIG.tasks[0].extra
    return NotionTextAnalysis(header, task_name, task_describe, database_id, extra_data)


def test_notion_text_analysis_init(notion_text_analysis):
    assert notion_text_analysis.header == CONFIG.notion.header
    assert notion_text_analysis.task_name == CONFIG.tasks[0].name
    assert notion_text_analysis.task_describe == CONFIG.tasks[0].describe
    assert notion_text_analysis.database_id == CONFIG.tasks[0].database_id
    assert notion_text_analysis.extra_data == CONFIG.tasks[0].extra
    assert notion_text_analysis.total_texts != []


def test_notion_text_analysis_run(notion_text_analysis):
    notion_text_analysis.run(
        stopwords=set(),
        output_dir=PROJECT_ROOT_DIR / "results",
        top_n=5,
        split_pkg="jieba",
    )
    assert not notion_text_analysis.tf_idf_dataframe.empty


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
        notion_text_analysis.handling_sentences(stopwords=set(), split_pkg="jieba")
    notion_text_analysis.total_texts = [["今天天气不错，适合出去玩", "#hello"]]
    with pytest.raises(NLPError):
        notion_text_analysis.handling_sentences(
            stopwords={"今天天气", "不错", "，", "适合", "出去玩"}, split_pkg="jieba"
        )
    notion_text_analysis.total_texts = [["#hello"]]
    with pytest.raises(NLPError):
        notion_text_analysis.handling_sentences(stopwords=set(), split_pkg="jieba")


class TestNotionDBText:
    def setup_class(self):
        self.header = CONFIG.notion.header
        self.database_id = CONFIG.tasks[0].database_id
        self.extra_data = CONFIG.tasks[0].extra
        self.db_text = NotionDBText(self.header, self.database_id, self.extra_data)

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
        name="test", describe="testing", database_id="123", extra=[], run=True
    )


def test_run_task_inputs(mock_task):
    # 测试函数输入的参数和异常情况
    with pytest.raises(ConfigError, match="Task or Task Name, there must be one."):
        run_task(task=None, task_json=None, task_name=None, config_file=config_file)

    with pytest.raises(ConfigError, match="Invalid task json."):
        run_task(task_json="{invalid json}", config_file=config_file)

    with pytest.raises(TaskError, match="nonexistent does not exist."):
        run_task(task_name="nonexistent", config_file=config_file)

    with pytest.raises(
        TaskError,
        match="discarded_task has been set to stop running. Check the parameters.",
    ):
        mock_task.run = False
        run_task(task_name="discarded_task", config_file=config_file)

    with pytest.raises(ConfigError, match="Token is required."):
        run_task(task_json="{valid json}", config_file="nonexistent")


def test_run_task_outputs():
    import shutil

    # 测试函数输出的结果类型和内容是否正确
    output_dir = Path("./unittest_results")
    while output_dir.exists():
        output_dir = output_dir / "subdir"
    run_task(
        task=CONFIG.tasks[0], config_file=config_file, output_dir=output_dir.as_posix()
    )

    # 测试输出结果是否正确
    # 此处的假设是notion_text_analysis.run()会在output_dir下生成一个文件
    assert (
        output_dir
        / f"{CONFIG.tasks[0].name}.tf_idf.analysis_result.top5_word_with_sentences.md"
    ).exists()
    # 删除文件
    shutil.rmtree(output_dir)


def test_run_task_subfunctions(mock_task):
    # 测试函数调用的子函数能否正常调用并返回正确的结果
    config_file = "configs/config.test.yaml"
    stopfiles_dir = "resources/stopwords"
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


def test_run_all_tasks():
    # 测试从文件运行
    run_all_tasks(config_file=PROJECT_ROOT_DIR / "configs/config.test.yaml")


if __name__ == "__main__":
    config_log(
        PROJECT_ROOT_DIR.stem,
        "unit_test",
        log_root=(PROJECT_ROOT_DIR / "logs").as_posix(),
        print_terminal=True,
        enable_monitor=False,
    )
    pytest.main(["-v", "-s", "-q", "test_notion_nlp.py"])
