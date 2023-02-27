import pytest
import json
from unittest.mock import MagicMock
from notion_nlp.core.api import NotionDBText


class TestNotionDBText:
    def test_read_pages_success(self):
        # 创建一个伪造的NotionParams实例
        mock_params = MagicMock()
        mock_params.url_get_pages = "http://fakeurl.com/get_pages"
        mock_params.header = {"Authorization": "Bearer fake_token"}
        mock_params.extra = {"start_cursor": ""}
        mock_params.database_id = "fake_database_id"

        # 创建一个伪造的响应结果
        fake_response = {
            "results": [
                {
                    "id": "page1_id",
                    "properties": {"title": {"title": [{"plain_text": "page1"}]}},
                },
                {
                    "id": "page2_id",
                    "properties": {"title": {"title": [{"plain_text": "page2"}]}},
                },
            ],
            "has_more": False,
            "next_cursor": "",
        }

        # 创建一个伪造的requests.post()函数，返回伪造的响应结果
        fake_post = MagicMock(return_value=MagicMock(text=json.dumps(fake_response)))

        # 替换原函数，使用伪造的参数和返回值
        notiondbtext = NotionDBText(mock_params)
        notiondbtext.read_pages = fake_post

        # 进行测试
        notiondbtext.read()
        assert notiondbtext.total_pages == fake_response["results"]

    def test_read_blocks_success(self):
        # 创建一个伪造的NotionParams实例
        mock_params = MagicMock()
        mock_params.url_get_blocks = "http://fakeurl.com/get_blocks"
        mock_params.header = {"Authorization": "Bearer fake_token"}
        mock_params.page_id = "fake_page_id"

        # 创建一个伪造的响应结果
        fake_response = {
            "results": [
                {
                    "id": "block1_id",
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"plain_text": "block1"}]},
                },
                {
                    "id": "block2_id",
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"plain_text": "block2"}]},
                },
            ]
        }

        # 创建一个伪造的requests.get()函数，返回伪造的响应结果
        fake_get = MagicMock(return_value=MagicMock(text=json.dumps(fake_response)))

        # 替换原函数，使用伪造的参数和返回值
        notiondbtext = NotionDBText(mock_params)
        notiondbtext.read_blocks = lambda pages: [fake_get() for _ in pages]

        # 进行测试
        notiondbtext.total_pages = [{"id": "page1_id"}, {"id": "page2_id"}]
        notiondbtext.read()
        assert notiondbtext.total_blocks == [fake_response, fake_response]

    def test_read_rich_text_success(self):
        # 创建一个伪造的NotionParams实例
        mock_params = MagicMock()
        mock_params.block_types = {"paragraph", "heading_1"}

        # 创建一个伪造的响应结果
        fake_blocks = [
            [
                {
                    "id": "block1_id",
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"plain_text": "block1"}]},
                }
            ],
            [
                {
                    "id": "block2_id",
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"plain_text": "block2"}]},
                },
                {
                    "id": "block3_id",
                    "type": "unsupported_type",
                    "unsupported_type": {"rich_text": [{"plain_text": "block3"}]},
                },
            ],
        ]

        # 创建一个伪造的requests.get()函数，返回伪造的响应结果
        fake_get = MagicMock(return_value=MagicMock(text=json.dumps(fake_blocks)))

        # 替换原函数，使用伪造的参数和返回值
        notiondbtext = NotionDBText(mock_params)
        notiondbtext.read_rich_text = lambda blocks: [fake_get() for _ in blocks]

        # 进行测试
        notiondbtext.total_pages = [{"id": "page1_id"}, {"id": "page2_id"}]
        notiondbtext.read()
        assert notiondbtext.total_blocks == [fake_blocks, fake_blocks]


if __name__ == "__main__":
    pytest.main(["-v", "-s", "-q", "test_api.py"])
