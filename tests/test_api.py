import pytest
import json
from unittest.mock import MagicMock, patch
from notion_nlp.core.api import NotionDBText


@pytest.fixture(scope="class")
def mock_params(request):
    # 创建一个伪造的NotionParams实例
    mock_params = MagicMock()
    mock_params.header = {"Authorization": "Bearer fake_token"}
    mock_params.extra = {"start_cursor": ""}
    mock_params.database_id = "fake_database_id"
    mock_params.page_id = "fake_page_id"
    mock_params.url_get_pages = "http://fakeurl.com/get_pages"
    mock_params.url_get_blocks = "http://fakeurl.com/get_blocks"
    mock_params.block_types = {"paragraph", "heading_1"}
    request.cls.params = mock_params


@pytest.mark.usefixtures("mock_params")
class TestNotionDBText:
    # @patch("notion_nlp.core.api.requests.post")
    @patch("requests.post")
    def test_read_pages_success(self, mock_post):
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
        # 替换原函数，使用伪造的参数和返回值
        notiondbtext = NotionDBText(self.params)
        # notiondbtext.read_pages = mock_post

        # 创建一个伪造的requests.post()函数，返回伪造的响应结果
        mock_post.return_value.text = json.dumps(fake_response, ensure_ascii=False)
        # mocker.patch("notiondbtext.read_pages", return_value=json.dumps(fake_response))

        # 进行测试
        assert notiondbtext.read_pages() == fake_response["results"]

    @patch("requests.get")
    def test_read_blocks_success(self, mock_get):
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
        mock_get.return_value.text = json.dumps(fake_response, ensure_ascii=False)

        # 替换原函数，使用伪造的参数和返回值
        notiondbtext = NotionDBText(self.params)
        # notiondbtext.read_blocks = lambda pages: [mock_get() for _ in pages]

        # 进行测试
        notiondbtext.total_pages = [{"id": "page1_id"}, {"id": "page2_id"}]
        assert notiondbtext.read_blocks() == [
            fake_response["results"],
            fake_response["results"],
        ]

    def test_read_rich_text_success(self):
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
        # 替换原函数，使用伪造的参数和返回值
        notiondbtext = NotionDBText(self.params)

        # 进行测试
        notiondbtext.total_blocks = fake_blocks
        assert notiondbtext.read_rich_text() == [["block1"], ["block2"]]


if __name__ == "__main__":
    pytest.main(["-v", "-s", __file__])
