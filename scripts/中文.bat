@echo off

color 0a

:main
echo ================= ☆ Notion 自然语言处理 ☆ =====================
echo=
echo 作者:  Dario Zhang
echo 版本:  v1.0.5.1
echo 代码:  https://github.com/dario-github/notion-nlp
echo 描述:  从Notion数据库中读取文本并进行自然语言处理分析
echo=
echo =====================   推广区   ==============================
echo=                                   
echo 激励作者:  https://reurl.cc/7R3MeN
echo=
echo ==============================================================
echo=
echo 1. 执行样例任务
echo 2. 查看任务信息
echo 3. 运行所有任务
echo 4. 运行单个任务
echo 5. 今日幸运事件

echo=
set /p opt=选项 （输入序号）：

if %opt% == 1 goto one
if %opt% == 2 goto two
if %opt% == 3 goto three
if %opt% == 4 goto four
if %opt% == 5 goto five

echo 无效选项
cls
goto main

:one
.\notion-nlp-win64.exe first-try || (set /p tmp=太可惜了~ 未知错误，请责令作者处理，记得复制上面的错误日志哦~ 到这里粘贴日志 ==> https://reurl.cc/b7nDkl && exit)
start notepad ".\Temp-dataset\configs\notion.test.yaml"
start explorer ".\Temp-dataset\results"
echo 已打开参数文件样例与生成结果样例，请参照使用说明修改参数文件：https://github.com/dario-github/notion-nlp/blob/main/README.zh.md#%E4%BD%BF%E7%94%A8 
set /p tmp=执行完毕，请按回车键返回菜单...
cls
goto main

:two
set /p file=请输入参数文件地址 [Default: .\Temp-dataset\configs\notion.yaml]: 
if not defined file set file=.\Temp-dataset\configs\notion.yaml
.\notion-nlp-win64.exe task-info --config-file %file% || ((echo 未找到参数文件或配置错误) && (goto two))
set /p tmp=执行完毕，请按回车键返回菜单...
cls
goto main

:three
set /p file=请输入参数文件地址 [Default: .\Temp-dataset\configs\notion.yaml]: 
if not defined file set file=.\Temp-dataset\configs\notion.yaml
.\notion-nlp-win64.exe run-all-tasks --config-file %file% || ((echo 未找到参数文件或配置错误) && (goto three))
set /p tmp=执行完毕，请按回车键返回菜单...
cls
goto main

:four
set /p name=请输入参数文件中的任务名
if not defined four goto four
set /p file=请输入参数文件地址 [Default: .\Temp-dataset\configs\notion.yaml]: 
if not defined file set file=.\Temp-dataset\configs\notion.yaml
.\notion-nlp-win64.exe run-task --task-name %name% --config-file %file%  || ((echo 未找到参数文件或配置错误) && (goto four))
set /p tmp=执行完毕，请按回车键返回菜单...
cls
goto main

:five
color 2
echo 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0
ping localhost -n 1 >nul
echo 2 1 3 2 1 3 2 1 3 2 1 3 2 1 3 2 1 3 2 1 3 2 1 3 2 1 2 3 1 5 4 6 4 6 5 4 6 5 4
ping localhost -n 1 >nul
echo 7 9 4 6 5 4 9 8 7 4 1 6 5 4 9 8 7 4 6 8 7 4 6 5 1 3 5 4 9 8 7 4 1 1 3 2 1 3 1
ping localhost -n 1 >nul
echo 1 3 5 4 1 6 5 4 6 1 3 2 4 8 6 4 3 5 4 1 6 5 4 6 1 3 8 7 4 6 5 4 5 4 6 8 1 3 5
ping localhost -n 1 >nul
echo 7 1 9 1 8 7 3 4 2 5 7 8 4 1 3 6 5 7 8 4 1 3 5 4 9 4 1 9 8 7 3 8 7 9 8 7 4 5 6
ping localhost -n 1 >nul
goto five

