#!/bin/bash

echo -e "\033[0;32m"

if [ ! -f "./tmp-dataset/configs/config.yaml" ]; then
echo "检测到脚本首次执行，将下载资源文件并执行引导，请耐心等待 1-3 min..."
./notion-nlp-linux first-try
if [ $? -ne 0 ]; then
echo "发现未知错误...请责令作者处理，记得复制上面的错误日志哦~到这里粘贴日志 ==> https://reurl.cc/b7nDkl"
read -p "请按任意键退出脚本..." tmp
exit 1
fi
echo "样例任务已执行完毕，请按回车键查看词云图样例及目录"
read -p "查看样例效果后请返回本窗口，继续下一步骤..." tmp
xdg-open "./tmp-dataset/results/wordcloud/chinese-simple_task"
echo
read -p "请按回车键查看主题总结markdown文档..." tmp
xdg-open "./tmp-dataset/results/tfidf_analysis/chinese-simple_task/chinese-simple_task.top_5.md"
echo
echo "如何配置自己的任务？教程指引 ==> https://github.com/dario-github/notion-nlp/blob/main/README.zh.md#%E4%BD%BF%E7%94%A8"
echo
read -p "请按回车键打开参数文件，开始配置您自己的任务..." tmp
cp -f "./tmp-dataset/configs/config.test.yaml" "./tmp-dataset/configs/config.yaml"
xdg-open "./tmp-dataset/configs/config.yaml"
echo
read -p "请按回车键进入主菜单..." tmp
clear
else
echo
fi

echo -e "\033[0;32m"