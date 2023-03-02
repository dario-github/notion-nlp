#!/bin/bash

# Get current working directory with full path
fullPath=$(pwd)

# Get only directory name without path
dirNameOrigin=$(basename $fullPath)
dirName=${dirNameOrigin//-/_}
echo $dirName
# pypi token
pypi_token=$(cat PYPI_TOKEN)

# 从__init__.py文件中读取版本信息
version=$(python -c "from src.$dirName import __version__; print(__version__)")
echo $version

# build & publish
/usr/bin/python3.8 -m poetry build && \
/usr/bin/python3.8 -m poetry publish -u __token__ -p $pypi_token

# pyinstaller linux exec file
/usr/bin/python3.8 -m poetry run pyinstaller -F src/$dirName/__main__.py -n $dirNameOrigin-linux && \

# Compress the executable file
zip -j ./dist/$dirNameOrigin-$version-linux.zip ./dist/$dirNameOrigin-linux ./scripts/Chinese-simple.sh scripts/English.sh scripts/start.sh

zip -j ./dist/$dirNameOrigin-$version-win64.zip ./dist/$dirNameOrigin-win64.exe scripts/Chinese-simple.bat scripts/English.bat scripts/start.bat

# todo 把停用词也更新了