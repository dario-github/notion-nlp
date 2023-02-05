# notion_api

读取notion数据库的富文本信息，并做简单的NLP分析

```mermaid
flowchart TB

A[(Notion Database)] --> B([通过 API 读取富文本]) --> C([分词 清洗 建立词句映射]) --> D([计算 TF-IDF]) --> E([将 top 关键词及对应语句输出为 markdown 格式])
```

## 依赖

```shell
pip install arrow ruamel.yaml tqdm pandas pyfunctional scikit-learn jieba
```

## 快速使用

## 问题

- jieba分词的准确率不高，可以替换为pkuseg，我的VPS配置不够运行pkuseg库（kernel died），所以如果条件允许可以更换为该库。

- tf-idf的分析方法