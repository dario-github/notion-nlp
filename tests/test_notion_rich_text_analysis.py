import logging
from pathlib import Path

import pytest

from notion_rich_text_analysis.parameter.utils import load_config
from notion_rich_text_analysis.__main__ import run_all_task
from notion_rich_text_analysis.parameter.log import config_log
from notion_rich_text_analysis.notion_db_text import NotionDBText
from notion_rich_text_analysis.notion_text_analysis import NotionTextAnalysis

PROJECT_ROOT_DIR = Path(__file__).parent.parent


def test_NotionDBText():
    """测试NotionDBText"""
    # 测试用参数文件
    config_file = PROJECT_ROOT_DIR / "configs/config.test.yaml"
    config = load_config(config_file)

    # NotionDBText初始化参数
    header = {k: str(v) for k, v in config["notion"]["header"]._items()}
    task = config["task"][0]
    database_id = task["database_id"]
    extra_data = task["extra"]

    # 读取DB
    notion_db_text = NotionDBText(header, database_id, extra_data)
    notion_db_text.read()
    logging.info(f"page sample: {notion_db_text.total_pages[0]}")

    # 一些显而易见的断言，确保NotionDBText确实能读取到数据
    assert len(notion_db_text.total_pages) > 0
    assert len(notion_db_text.total_blocks) > 0
    assert len(notion_db_text.total_texts) > 0

    logging.info(
        f"{len(notion_db_text.total_texts)} texts. sample: {notion_db_text.total_texts[0][0]}"
    )


def test_run_all_task():
    run_all_task(config_file=PROJECT_ROOT_DIR / "configs/config.test.yaml")


if __name__ == "__main__":
    config_log(
        PROJECT_ROOT_DIR.stem,
        "unit_test",
        log_root=(PROJECT_ROOT_DIR / "logs").as_posix(),
        print_terminal=True,
        enable_monitor=False,
    )
    pytest.main(["-v", "-s", "-q", "test_notion_rich_text_analysis.py"])
