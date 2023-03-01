@echo off

color 0a
:: First run of the script: download resource files
if not exist ".\Temp-dataset\configs\config.yaml" (
echo Detected first run of the script, will download resource files and execute the guide, please wait patiently for 1-3 min...
.\notion-nlp-win64.exe first-try
IF NOT %ERRORLEVEL% EQU 0 (
echo "Unknown error found...Please ask the author to handle it, and remember to copy the error log above~Paste the log here ==> https://reurl.cc/b7nDkl"
set /p tmp=Press any key to exit the script...
exit)
echo Example task has been executed, please press Enter to see the word cloud example and directory
set /p tmp=After viewing the sample effect, please return to this window to continue to the next step...
:: start "" ".\Temp-dataset\results\wordcloud\chinese-simple_task\colormap_viridis.png"
start "" ".\Temp-dataset\results\wordcloud\chinese-simple_task"
echo=
set /p tmp=Press Enter to view the summary markdown document of the topic...
start "" ".\Temp-dataset\results\tfidf_analysis\chinese-simple_task\chinese-simple_task.top_5.md"
echo=
echo "How to configure your own task? Tutorial guidance ==> https://reurl.cc/NqAybp"
echo=
set /p tmp=Press Enter to open the parameter file and start configuring your own task...
copy /y ".\Temp-dataset\configs\config.test.yaml" ".\Temp-dataset\configs\config.yaml" > nul
start "" ".\Temp-dataset\configs\config.yaml"
echo=
echo /p tmp=Press Enter to enter the main menu...
cls
) else (
echo=
)

color 0a
:main
color 0a

echo ============  Notion Natural Language Processing  =================
echo=
echo Author:      Dario Zhang
echo Version:     v1.0.7.2
echo Code:        https://github.com/dario-github/notion-nlp
echo Description: Read text from the Notion database and perform natural
echo              language processing analysis
echo=
echo ===================== Promotion Zone ==============================
echo=
echo Support the author: https://reurl.cc/7R3MeN
echo=
echo ===================================================================
echo=
echo 1. View task information
echo 2. Run all tasks
echo 3. Run a specific task
echo 4. Watch the Lucky Parrot

echo=
set /p opt=Option (Enter the number):

if %opt% == 1 goto one
if %opt% == 2 goto two
if %opt% == 3 goto three
if %opt% == 4 goto lastopt

echo Invalid option
cls
goto main

:: View task information
:one
.\notion-nlp-win64.exe task-info --config-file ".\Temp-dataset\configs\config.yaml"
IF %ERRORLEVEL% EQU 0 GOTO endresult
echo Parameter file not found or configuration error, please check the configuration file according to the tutorial
goto main

:: Execute all tasks
:two
.\notion-nlp-win64.exe run-all-tasks --config-file ".\Temp-dataset\configs\config.yaml"
IF %ERRORLEVEL% EQU 0 GOTO endresult
echo Parameter file not found or configuration error, please check the configuration file according to the tutorial
goto main

:: Execute a single task
:three
set /p name=Please enter the task name from the parameter file. If the name contains spaces, please enclose it in double quotes. Enter "info" to view all task information:
if not defined name goto three
if %name% == info goto one
.\notion-nlp-win64.exe run-task --task-name %name% --config-file ".\Temp-dataset\configs\config.yaml"
IF %ERRORLEVEL% EQU 0 GOTO endresult
echo Parameter file not found or configuration error. Please check the configuration file according to the tutorial.
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
set /p tmp=Execution completed. Press Enter to return to the menu...
cls
goto main

:lastopt
start parrot.bat
cls
goto main
