#!/bin/bash

# dir name
dir=$(basename $(dirname $0))

# pypi token
pypi_token=$(cat PYPI_TOKEN)

# 从__init__.py文件中读取版本信息
version=$(python -c "from src.$dir import __version__; print(__version__)")

# build & publish
poetry build && \
poetry publish -u __token__ -p $pypi_token

# pyinstaller linux exec file
pyinstaller -F src/$dir/__main__.py -n $dir-linux && \

# Compress the executable file
zip ./dist/$dir-linux.zip ./dist/$dir-linux ./scripts/Chinese-simple.sh scripts/English.sh scripts/start.sh

zip dist/$dir-win64.zip dist/$dir-win64.exe scripts/Chinese-simple.bat scripts/English.bat scripts/start.bat