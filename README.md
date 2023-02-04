# notion_api

读取notion数据库的富文本信息，并做NLP分析

```mermaid
flowchart TB

A[(Notion Database)] --> B([通过 API 读取富文本]) --> C([分词 清洗 建立词句映射]) --> D([计算 TF-IDF]) --> E([将 top 关键词及对应语句输出为 markdown 格式])
```
