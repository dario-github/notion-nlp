from pathlib import Path
import pytest

from notion_nlp.parameter.utils import load_config
from notion_nlp.core.task import check_resource

from notion_nlp.parameter.config import (
    PathParams,
)
from notion_nlp.parameter.error import NLPError
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
