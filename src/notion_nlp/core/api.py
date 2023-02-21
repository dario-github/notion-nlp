import json
import logging
import ssl
from typing import List

import arrow
import requests
from tqdm import tqdm

# from requests.adapters import HTTPAdapter
# from requests.packages.urllib3.util.retry import Retry
# retry_strategy = Retry(
#     total=10, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504]
# )

# adapter = HTTPAdapter(max_retries=retry_strategy)
# http = requests.Session()
# http.mount("https://", adapter)


class NotionDBText:
    """
    读取数据库中所有富文本信息
    """

    def __init__(self, header: dict, database_id: str, extra_data: dict = dict()):
        self.header = header
        self.database_id = database_id
        self.extra_data = extra_data
        self.total_texts, self.total_blocks, self.total_pages = [[]] * 3
        self.block_types = [
            "paragraph",
            "bulleted_list_item",
            "numbered_list_item",
            "toggle",
            "to_do",
            "quote",
            "callout",
            "synced_block",
            "template",
            "column",
            "child_page",
            "child_database",
            "table",
            "heading_1",
            "heading_2",
            "heading_3",
        ]

    def read(self):
        self.total_pages = self.read_pages()
        self.total_blocks = self.read_blocks(self.total_pages)
        self.total_texts = self.read_rich_text(self.total_blocks)

    def read_pages(self):
        """
        读取database中所有pages
        """
        total_pages = []
        passed_pages = 0
        has_more = True
        next_cursor = ""
        # 有下一页时，继续读取
        while has_more:
            if next_cursor:
                self.extra_data["start_cursor"] = next_cursor
            try:
                r_database = requests.post(
                    url=f"https://api.notion.com/v1/databases/{self.database_id}/query",
                    headers=self.header,
                    data=json.dumps(self.extra_data),
                )
            except ssl.SSLEOFError:
                logging.error(f"read page failed, database id: {self.database_id}")
                passed_pages += 1
            else:
                respond = json.loads(r_database.text)
                total_pages.extend(respond["results"])
                has_more = respond["has_more"]
                next_cursor = respond["next_cursor"]
        logging.info(f"{len(total_pages)} pages in task when {arrow.now()}")
        logging.info(f"{passed_pages} pages passed when {arrow.now()}")
        return total_pages

    def read_blocks(self, pages: List):
        """
        读取pages中所有blocks
        """
        total_blocks = []
        passed_blocks = 0
        for page in tqdm(pages, desc="read blocks"):
            page_id = page["id"]
            try:
                r_page = requests.get(
                    url=f"https://api.notion.com/v1/blocks/{page_id}/children",
                    headers=self.header,
                )
            except ssl.SSLEOFError:
                logging.error(f"read block failed, page id: {page_id}")
                passed_blocks += 1
            else:
                total_blocks.append(json.loads(r_page.text).get("results", []))
        logging.info(f"passed {passed_blocks} blocks")
        return total_blocks

    def read_rich_text(self, blocks: List):
        """
        读取blocks中所有rich text
        """
        total_texts = []
        passed_texts = 0
        self.unsupported_types = set()
        for page_blocks in blocks:
            page_texts = []
            for block in page_blocks:
                if block["type"] not in self.block_types:
                    self.unsupported_types.add(block["type"])
                    continue
                try:
                    page_texts.extend(
                        [x["plain_text"] for x in block[block["type"]]["rich_text"]]
                    )
                except KeyError:
                    logging.error(block["type"] + "|" + json.dumps(block[block["type"]]))
                    passed_texts += 1
            total_texts.append(page_texts)
        logging.info(
            f"{sum([len(x) for x in total_texts])} texts in task when {arrow.now()}"
        )
        logging.info(f"{passed_texts} texts passed when {arrow.now()}")
        return total_texts
