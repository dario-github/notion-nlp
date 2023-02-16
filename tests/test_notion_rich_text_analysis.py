from pathlib import Path

import pytest

from notion_rich_text_analysis.__main__ import run_all_task
from notion_rich_text_analysis.parameter.log import config_log


def test_run_all_task():
    project_dir = Path(__file__).parent.parent
    config_log(
        project_dir.stem,
        "test_run_all_task",
        log_root=(project_dir / "logs").as_posix(),
        print_terminal=True,
        enable_monitor=False,
    )
    run_all_task(config_file=project_dir / "config/config.test.yaml")


if __name__ == "__main__":
    pytest.main(["-v", "-s", "-q", "test_notion_rich_text_analysis.py"])
