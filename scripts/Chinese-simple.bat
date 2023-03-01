@echo off

color 0a
:: 首次执行脚本：下载资源文件
if not exist ".\Temp-dataset\configs\config.yaml" (
    echo 检测到脚本首次执行，将下载资源文件并执行引导，请耐心等待 1-3 min...
    .\notion-nlp-win64.exe first-try
    IF NOT %ERRORLEVEL% EQU 0 (
      echo "发现未知错误...请责令作者处理，记得复制上面的错误日志哦~到这里粘贴日志 ==> https://reurl.cc/b7nDkl"
      set /p tmp=请按任意键退出脚本...
      exit)
    echo 样例任务已执行完毕，请按回车键查看词云图样例及目录
    set /p tmp=查看样例效果后请返回本窗口，继续下一步骤...
    start "" ".\Temp-dataset\results\wordcloud\chinese-simple_task"
    echo=
    set /p tmp=请按回车键查看主题总结markdown文档...
    start "" ".\Temp-dataset\results\tfidf_analysis\chinese-simple_task\chinese-simple_task.top_5.md"
    echo=
    echo "如何配置自己的任务？教程指引 ==> https://reurl.cc/NqAybp"
    echo=
    set /p tmp=请按回车键打开参数文件，开始配置您自己的任务...
    copy /y ".\Temp-dataset\configs\config.test.yaml" ".\Temp-dataset\configs\config.yaml" > nul
    start "" ".\Temp-dataset\configs\config.yaml"
    echo=
    echo /p tmp=请按回车键进入主菜单...
    cls
) else (
    echo=
)

color 0a
:main
color 0a
echo=
echo ================== ☆ Notion 自然语言处理 ☆ ======================
echo=
echo 作者:  Dario Zhang
echo 版本:  v1.0.7.2
echo 代码:  https://github.com/dario-github/notion-nlp
echo 描述:  从Notion数据库中读取文本并进行自然语言处理分析
echo=
echo =========================   推广区   ============================
echo=                                   
echo 激励作者:  https://reurl.cc/7R3MeN
echo=
echo ===============================================================
echo=
echo 1. 查看任务信息
echo 2. 运行所有任务
echo 3. 运行指定任务
echo 4. 观赏幸运鹦鹉

echo=
set /p opt=选项 (输入序号):

if %opt% == 1 goto one
if %opt% == 2 goto two
if %opt% == 3 goto three
if %opt% == 4 goto lastopt

echo 无效选项
cls
goto main

:: 查看任务信息
:one
.\notion-nlp-win64.exe task-info --config-file ".\Temp-dataset\configs\config.yaml"
IF %ERRORLEVEL% EQU 0 GOTO endresult
echo 未找到参数文件或配置错误，请按照教程检查配置文件
goto main

:: 执行所有任务
:two
.\notion-nlp-win64.exe run-all-tasks --config-file ".\Temp-dataset\configs\config.yaml"
IF %ERRORLEVEL% EQU 0 GOTO endresult
echo 未找到参数文件或配置错误，请按照教程检查配置文件
goto main

:: 执行单个任务
:three
set /p name=请输入参数文件中的任务名，如包含空格，请用双引号包裹任务名，输入 info 查看所有任务信息: 
if not defined name goto three
if %name% == info goto one
.\notion-nlp-win64.exe run-task --task-name %name% --config-file ".\Temp-dataset\configs\config.yaml"
IF %ERRORLEVEL% EQU 0 GOTO endresult
echo 未找到参数文件或配置错误，请按照教程检查配置文件
goto main


:endresult
echo=
echo  ██████╗ ██╗  ██╗
echo ██╔═══██╗██║ ██═╝
echo ██║   ██║████║
echo ██║   ██║██║ ██╗
echo ╚██████╔╝██║╗ ██╗
echo  ╚═════╝ ╚══╝ ╚═╝
echo=
set /p tmp=执行完毕，请按回车键返回菜单...
cls
goto main


:lastopt
start parrot.bat
cls
goto main
