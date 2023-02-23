import json
import logging
from typing import List

import arrow
import requests
from tqdm import tqdm

from notion_nlp.parameter.config import NotionParams

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

    def __init__(self, header: dict, database_id: str, extra_data: dict = {}):
        self.header = header  # todo 改为获取token？，header是API类自带的属性，不应该从外部获取
        self.database_id = database_id
        self.extra_data = extra_data
        self.total_texts, self.total_blocks, self.total_pages = [[]] * 3
        self.api_params = NotionParams()
        self.api_params.database_id = database_id

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
                    url=self.api_params.url_get_pages,
                    headers=self.header,
                    data=json.dumps(self.extra_data),
                )
            except Exception:
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
            self.api_params.page_id = page_id
            try:
                r_page = requests.get(
                    url=self.api_params.url_get_blocks,
                    headers=self.header,
                )
            except Exception:
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
                if block["type"] not in self.api_params.block_types:
                    self.unsupported_types.add(block["type"])
                    continue
                try:
                    page_texts.extend(
                        [x["plain_text"] for x in block[block["type"]]["rich_text"]]
                    )
                except KeyError:
                    logging.error(
                        "No plain text in type: "
                        + block["type"]
                        + "|"
                        + json.dumps(block[block["type"]])
                    )
                    passed_texts += 1
            total_texts.append(page_texts)
        logging.info(
            f"{sum([len(x) for x in total_texts])} texts in task when {arrow.now()}"
        )
        logging.info(f"{passed_texts} texts passed when {arrow.now()}")
        return total_texts
