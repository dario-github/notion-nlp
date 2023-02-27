from unittest.mock import patch
from pathlib import Path
import pytest
import json
import ssl

from notion_nlp.parameter.utils import load_config, load_stopwords
from notion_nlp.core.task import run_task, run_all_tasks, check_resource

from notion_nlp.parameter.config import (
    TaskParams,
    ConfigParams,
    PathParams,
    NotionParams,
    APIParams,
    NLPParams,
)
from notion_nlp.parameter.log import config_log
from notion_nlp.parameter.error import NLPError, ConfigError, TaskError
from notion_nlp.core.api import NotionDBText
from notion_nlp.core.nlp import NotionTextAnalysis
from memory_profiler import profile

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
    return NotionTextAnalysis(task)


def test_notion_text_analysis_init(notion_text_analysis):
    assert notion_text_analysis.total_texts != []


def test_notion_text_analysis_check_stopwords(notion_text_analysis):
    assert notion_text_analysis.check_stopwords("the", {"the", "is"}) is True
    assert notion_text_analysis.check_stopwords("123", {"the", "is"}) is True
    assert notion_text_analysis.check_stopwords("", {"the", "is"}) is True
    assert notion_text_analysis.check_stopwords("hello", {"the", "is"}) is False


def test_notion_text_analysis_check_sentence_available(notion_text_analysis):
    assert notion_text_analysis.check_sentence_available("#hello world!") is False
    assert notion_text_analysis.check_sentence_available("hello world!") is True


def test_notion_text_analysis_split_sentence(notion_text_analysis):
    assert notion_text_analysis.split_sentence("今天天气不错，适合出去玩", "jieba") == [
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


# @pytest.fixture
# def mock_task():
#     # 定义一个mock task用于测试
#     return TaskParams(
#         name="test",
#         description="testing",
#         api=APIParams(notion=NotionParams(database_id="123")),
#         run=True,
#     )


def test_run_task_with_valid_task(notion_config):
    # Create a valid task object
    task = notion_config.tasks[0]
    # Call your function with the task object
    run_task(
        task=task, config_file=PROJECT_ROOT_DIR / PathParams.notion_test_config.value
    )
    # Check if the output directory contains the expected files
    assert Path(EXEC_DIR / PathParams.tfidf_analysis.value).exists()


def test_run_task_with_invalid_task(mock_task):
    # Create an invalid task object (missing token)
    run_task(
        task=mock_task, config_file=PROJECT_ROOT_DIR / PathParams.notion_test_config.value
    )


def test_run_task_with_no_input():
    # Call your function with no input arguments and expect an exception
    with pytest.raises(ConfigError):
        run_task()


if __name__ == "__main__":
    config_log(
        EXEC_DIR.stem,
        "unit_test",
        log_root=(EXEC_DIR / "logs").as_posix(),
        print_terminal=True,
        enable_monitor=False,
    )
    pytest.main(["-v", "-s", "-q", "test_notion_nlp.py"])
