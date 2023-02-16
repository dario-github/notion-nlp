import requests
import json
import arrow
from tqdm import tqdm
from typing import List

# 日志模块
import logging
from notion_rich_text_analysis.parameter.log import config_log


class NotionDBText:
    """
    读取数据库中所有富文本信息
    """

    def __init__(self, header: dict, database_id: str, extra_data: dict = dict()):
        self.header = header
        self.database_id = database_id
        self.extra_data = extra_data
        self.total_texts, self.total_blocks, self.total_pages = [[]] * 3
        self.block_types = ["paragraph", "bulleted_list_item", "numbered_list_item",
                            "toggle", "to_do", "quote",
                            "callout", "synced_block", "template",
                            "column", "child_page", "child_database", "table",
                            "heading_1", "heading_2", "heading_3"]

    def read(self):
        self.total_pages = self.read_pages()
        self.total_blocks = self.read_blocks(self.total_pages)
        self.total_texts = self.read_rich_text(self.total_blocks)

    def read_pages(self):
        """
        读取database中所有pages
        """
        total_pages = []
        has_more = True
        next_cursor = ''
        # 有下一页时，继续读取
        while has_more:
            if next_cursor:
                self.extra_data['start_cursor'] = next_cursor
            r_database = requests.post(
                url=f"https://api.notion.com/v1/databases/{self.database_id}/query",
                headers=self.header,
                data=json.dumps(self.extra_data),
            )
            respond = json.loads(r_database.text)
            total_pages.extend(respond["results"])
            has_more = respond['has_more']
            next_cursor = respond['next_cursor']
        logging.info(f'{len(total_pages)} pages when {arrow.now()}')
        return total_pages

    def read_blocks(self, pages: List):
        """
        读取pages中所有blocks
        """
        total_blocks = []
        for page in tqdm(pages, desc='read blocks'):
            page_id = page["id"]
            r_page = requests.get(
                url=f"https://api.notion.com/v1/blocks/{page_id}/children",
                headers=self.header,
            )
            total_blocks.append(json.loads(r_page.text).get("results", []))
        return total_blocks

    def read_rich_text(self, blocks: List):
        """
        读取blocks中所有rich text
        """
        total_texts = []
        self.unsupported_types = set()
        for page_blocks in blocks:
            page_texts = []
            for block in page_blocks:
                if block['type'] not in self.block_types:
                    self.unsupported_types.add(block['type'])
                    continue
                try:
                    page_texts.extend([x['plain_text']
                                      for x in block[block['type']]['rich_text']])
                except KeyError:
                    logging.error(block['type'] + '|' +
                                  json.dumps(block[block['type']]))
            total_texts.append(page_texts)
        return total_texts
