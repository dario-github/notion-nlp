#!/bin/bash

# pypi token
pypi_token=$(cat PYPI_TOKEN)

# 从__init__.py文件中读取版本信息
version=$(python -c "from src.notion_nlp import __version__; print(__version__)")

# build & publish
poetry build && \
poetry publish -u __token__ -p $pypi_token

# pyinstaller linux exec file
pyinstaller -F src/notion_nlp/__main__.py -n notion-nlp-linux && \

# Compress the executable file
zip ./dist/notion-nlp-linux.zip ./dist/notion-nlp-linux ./scripts/Chinese-simple.sh scripts/English.sh scripts/start.sh

zip dist/notion-nlp-win64.zip dist/notion-nlp-win64.exe scripts/Chinese-simple.bat scripts/English.bat scripts/start.bat