#!/bin/bash

echo "================= ☆ Notion 自然语言处理 ☆ ====================="
echo ""
echo "作者: Dario Zhang"
echo "版本: v1.0.6"
echo "代码: https://github.com/dario-github/notion-nlp"
echo "描述: 从Notion数据库中读取文本并进行自然语言处理分析"
echo ""
echo "===================== 推广区 =============================="
echo ""
echo "激励作者: https://reurl.cc/7R3MeN"
echo ""
echo "=============================================================="
echo ""
echo "1. 执行样例任务"
echo "2. 查看任务信息"
echo "3. 运行所有任务"
echo "4. 运行单个任务"
echo "5. 今日幸运事件"
echo ""
read -p "选项（输入序号）：" opt

case $opt in
    1)
        ./notion-nlp-linux first-try || (read -p "太可惜了~ 未知错误，请责令作者处理，记得复制上面的错误日志哦~ 到这里粘贴日志 ==> https://reurl.cc/b7nDkl && exit")
        xdg-open "./Temp-dataset/configs/notion.test.yaml"
        xdg-open "./Temp-dataset/results"
        echo "已打开参数文件样例与生成结果样例，请参照使用说明修改参数文件：https://github.com/dario-github/notion-nlp/blob/main/README.zh.md#%E4%BD%BF%E7%94%A8"
        read -p "执行完毕，请按回车键返回菜单..." tmp
        clear
        ;;
    2)
        read -p "请输入参数文件地址 [Default: ./Temp-dataset/configs/notion.yaml]: " file
        file=${file:-"./Temp-dataset/configs/notion.yaml"}
        ./notion-nlp-linux64 task-info --config-file "$file" || (echo "未找到参数文件或配置错误" && continue)
        read -p "执行完毕，请按回车键返回菜单..." tmp
        clear
        ;;
    3)
        read -p "请输入参数文件地址 [Default: ./Temp-dataset/configs/notion.yaml]: " file
        file=${file:-"./Temp-dataset/configs/notion.yaml"}
        ./notion-nlp-linux64 run-all-tasks --config-file "$file" || (echo "未找到参数文件或配置错误" && continue)
        read -p "执行完毕，请按回车键返回菜单..." tmp
        clear
        ;;
    4)
        read -p "请输入参数文件中的任务名: " name
        if [ -z "$name" ]; then
            continue
        fi
        read -p "请输入参数文件地址 [Default: ./Temp-dataset/configs/notion.yaml]: " file
        file=${file:-"./Temp-dataset/configs/notion.yaml"}
        ./notion-nlp-linux64 run-task --task-name "$name" --config-file "$file" || (echo "未找到参数文件或配置错误" && continue)
        read -p "执行完毕，请按回车键返回菜单..." tmp
        clear
        ;;
    5)
        echo -e "\033[32m0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0\033[0m"
        sleep 1
        echo -e "\033[32m2 1 3 2 1 3 2 1 3 2 1 3 2 1 3 2 1 3 2 1 3 2 1 3 2 1 2 3 1 5 4 6 4 6 5 4 6 5 4\033["
        read -p "已执行完毕，请按回车键返回"
