# Text-Miner

A tool for mining valuable information from text using NLP techniques.

## Background

Text is one of the most common and rich sources of data in our daily life. However, extracting useful information from text can be challenging and time-consuming. Text-Miner is a tool that aims to simplify this process by using natural language processing (NLP) techniques to analyze text and extract topics, sentences, keywords, and sentiment.

## Features

Text-Miner can:

- Connect to various APIs such as note-taking software, social media platforms, etc. and fetch text data from them.
- Analyze the text data using NLP techniques such as topic modeling, named entity recognition, sentiment analysis, etc. and output the results in a structured format.
- Generate a markdown file that contains the top n topics and their corresponding sentences from the text data, as well as a word cloud image that visualizes all the topics.
- Support multiple languages such as English, 中文, 日本語, Español, Français or Deutsch.

## Installation and Usage

To install Text-Miner, you need to have Python 3.6 or higher installed on your system. You can use pip to install Text-Miner from PyPI:

```bash
pip install text-miner
```

To use Text-Miner, you need to provide a configuration file that specifies the source of your text data (such as an API key or a URL), the language of your text data (such as "en" or "zh"), and the number of topics you want to extract (such as 5 or 10). You can use JSON or YAML format for your configuration file. For example:

```json
{
    "source": "evernote",
    "api_key": "xxxxxxxxxxxxxxxxxxxxx",
    "language": "en",
    "topics": 5
}
```

Then you can run Text-Miner with your configuration file as an argument:

```bash
text-miner config.json
```

Text-Miner will output a markdown file named `text-miner.md` and a word cloud image named `text-miner.png` in your current directory.

## License and Contribution

Text-Miner is licensed under MIT License. If you want to contribute to Text-Miner or report any issues or suggestions, please visit <https://github.com/dario-github/text-miner>.
