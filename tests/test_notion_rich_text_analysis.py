import pytest

from notion_rich_text_analysis.notion_db_text import NotionDBText
from notion_rich_text_analysis.notion_text_analysis import NotionTextAnalysis

if __name__ == "__main__":
    pytest.main(["-v", "-s", "-q", "test_notion_rich_text_analysis.py"])
