<p align="center">
  <img width="100px" src="https://img.icons8.com/ios/250/FFFFFF/share-2.png" align="center" alt="Notion Rich Text Data Analysis" />
  <h1 align="center">
    Notion NLP
  </h1>
  <p align="center">
    To read text from a Notion database and perform natural language processing analysis.
  </p>
</p>

  <p align="center">
    <a href="https://github.com/dario-github/notion-nlp/actions">
      <img alt="Tests Passing" src="https://github.com/dario-github/notion-nlp/actions/workflows/main.yml/badge.svg" />
    </a>
    <a href="https://codecov.io/gh/dario-github/notion-nlp">
      <img alt="codecov" src="https://codecov.io/gh/dario-github/notion-nlp/branch/main/graph/badge.svg?token=ehzYhousD3" />
    </a>
    <a href="https://github.com/dario-github/notion-nlp/graphs/contributors">
      <img alt="GitHub Contributors" src="https://img.shields.io/github/contributors/dario-github/notion-nlp" />
    </a>
    <a href="https://visitorbadge.io/status?path=https%3A%2F%2Fgithub.com%2Fdario-github%2Fnotion-nlp">
      <img alt="visitors" src="https://api.visitorbadge.io/api/visitors?path=https%3A%2F%2Fgithub.com%2Fdario-github%2Fnotion-nlp&countColor=%2337d67a&style=flat" />
    </a>
  </p>
  
  <p align="center">
    <a href="README.md">English</a>
    /
    <a href="README.zh.md">简体中文</a>
  </p>

## Introduction

When flomo first came out, a database was built in notion to implement similar functionality. It has been a few years since I recorded my thoughts and summaries, and I have accumulated some corpus. flomo's roaming function is not very suitable for my needs, so I wanted to write my own small tool to access the notion API and do NLP analysis.

Last year I wrote a demo using a notebook, but I put it on hold for a while and then improved it. Currently, it supports batch analysis tasks, you can add multiple databases and properties in the configuration file to filter the sorting criteria, and then output the keywords and the corresponding statement paragraph markdown by TF-IDF.

For example, I have added the following task myself.

- Reflections from the last year
- Summary optimisation for the year
- Self-caution for all periods
- List for the week

## Pipline

<div style="text-align:center;">

```mermaid
flowchart TB

A[(Notion Database)] --> B([read rich text via API]) --> C([split word / cleaning / word-phrase mapping]) --> D[/calculate TF-IDF/] --> E[[Output the top-n keywords and their corresponding sentences in markdown format]]
```

</div>

## Installation

```shell
python3.8 -m pip install notion-nlp
```

## Quick use

Configuration file reference ``configs/config.sample.yaml`` (hereinafter config, please rename to ``config.yaml`` as your own configuration file)

### Get the integration token

In [notion integrations](https://www.notion.so/my-integrations/) create a new integration, get your own token and fill in the token in the config.yaml file afterwards.

> [graphic tutorial in tango website](https://app.tango.us/app/workflow/6e53c348-79b6-4ed3-8c75-46f5ddb996da?utm_source=markdown&utm_medium=markdown&utm_campaign=workflow%20export%20links) / [graphic tutorial in markdown format](./docs/tango/get_the_integration_token.md)

### Add integration to database/get database ID

If you open the notion database page in your browser or click on the share copy link, you will see the database id in the address link (similar to a string of jumbles) and fill in the database_id under the task of config.

> [graphic tutorial in tango website](https://app.tango.us/app/workflow/7e95c7df-af73-4748-9bf7-11efc8e24f2a?utm_source=markdown&utm_medium=markdown&utm_campaign=workflow%20export%20links) / [graphic tutorial in markdown format](./docs/tango/add_integration_to_database.md)

### Configure the filter sort database entry extra parameter

The task's extra is used to filter and sort the database, see [notion filter API](https://developers.notion.com/reference/post-database-query-filter#property-filter-object) for format and content, the [config.sample.yaml](./configs/config.sample.yaml) file already provides 2 configurations.

### Run all tasks

```shell
python3.8 -m notion-nlp run-all-tasks --config-file ${Your Config file Path}
```

## Development

Welcome to fork and add new features/fix bugs.

- After cloning the project, use the `create_python_env_in_new_machine.sh` script to create a Poetry virtual environment.

- After completing the code development, use the invoke command to perform a series of formatting tasks, including black/isort tasks added in task.py.
  
    ```shell
    invoke check
    ```

- After submitting the formatted changes, run unit tests to check coverage.

    ```shell
    poetry run tox

    ```

## Note

- The word segmentation tool has two built-in options: jieba/pkuseg. (Considering adding language analysis to automatically select the most suitable word segmentation tool for that language.)

  - jieba is used by default.
  - pkuseg cannot be installed with poetry and needs to be installed manually with pip. In addition, this library is slow and requires high memory usage. It has been tested that a VPS with less than 1G memory needs to load virtual memory to use it.

- The analysis method using tf-idf is too simple. Consider integrating the API of LLM (such as chatGPT) for further analysis.

## Contributions

- scikit-learn - [https://github.com/scikit-learn/scikit-learn](https://github.com/scikit-learn/scikit-learn)

## License and Copyright

- [MIT License](./LICENSE)
  - The MIT License is a permissive open-source software license. This means that anyone is free to use, copy, modify, and distribute your software, as long as they include the original copyright notice and license in their derivative works.

  - However, the MIT License comes with no warranty or liability, meaning that you cannot be held liable for any damages or losses arising from the use or distribution of your software.

  - By using this software, you agree to the terms and conditions of the MIT License.

## Contact information

- See more at my [HomePage](https://github.com/dario-github)
