import pytest
from pathlib import Path
from notion_nlp.parameter.config import TaskParams, APIParams, NotionParams, PathParams
from notion_nlp.parameter.error import NLPError, ConfigError, TaskError
from notion_nlp.core.task import run_task
from notion_nlp.parameter.utils import load_config

PROJECT_ROOT_DIR = Path(__file__).parent.parent
EXEC_DIR = Path.cwd()


@pytest.fixture
def notion_config():
    config_file = PROJECT_ROOT_DIR / PathParams.notion_test_config.value
    config = load_config(config_file)
    return config


@pytest.fixture
def mock_task():
    # 定义一个mock task用于测试
    return TaskParams(
        name="test",
        description="testing",
        api=APIParams(notion=NotionParams(token="fake_token", database_id="123")),
        run=True,
    )


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
    assert (
        run_task(
            task=mock_task,
            config_file=PROJECT_ROOT_DIR / PathParams.notion_test_config.value,
        )
        is False
    )


def test_run_task_with_no_input():
    # Call your function with no input arguments and expect an exception
    with pytest.raises(ConfigError):
        run_task()
