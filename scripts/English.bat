@echo off

color 0a

:main
echo ==================== �� Notion Natural Language Processing �� =====================
echo=
echo Author:      Dario Zhang
echo Version:     v1.0.6
echo Code:        https://github.com/dario-github/notion-nlp
echo Description: Read text from Notion database 
echo              and perform natural language processing analysis
echo=
echo ============================== Promotion area ====================================
echo=
echo Support author: https://reurl.cc/7R3MeN
echo=
echo ==================================================================================
echo=
echo 1. Execute example task
echo 2. View task information
echo 3. Run all tasks
echo 4. Run a single task
echo 5. Today's lucky event

echo=
set /p opt=Option (Enter the number):

if %opt% == 1 goto one
if %opt% == 2 goto two
if %opt% == 3 goto three
if %opt% == 4 goto four
if %opt% == 5 goto five

echo Invalid option
cls
goto main

:one
.\notion-nlp-win64.exe first-try || (set /p tmp=Oops~ Unknown error, please ask the author to handle it, and remember to copy the error log above~ Paste the log here ==> https://reurl.cc/b7nDkl && exit)
start notepad ".\Temp-dataset\configs\config.test.yaml"
start explorer ".\Temp-dataset\results"
echo The parameter file example and generated result example have been opened, please modify the parameter file according to the usage instructions: https://github.com/dario-github/notion-nlp/blob/main/README.zh.md#%E4%BD%BF%E7%94%A8
set /p tmp=Execution completed, press Enter to return to the menu...
cls
goto main

:two
set /p file=Please enter the parameter file path [Default: .\Temp-dataset\configs\config.yaml]:
if not defined file set file=.\Temp-dataset\configs\config.yaml
.\notion-nlp-win64.exe task-info --config-file %file% || ((echo Parameter file not found or configuration error) && (goto two))
set /p tmp=Execution completed, press Enter to return to the menu...
cls
goto main

:three
set /p file=Please enter the parameter file path [Default: .\Temp-dataset\configs\config.yaml]:
if not defined file set file=.\Temp-dataset\configs\config.yaml
.\notion-nlp-win64.exe run-all-tasks --config-file %file% || ((echo Parameter file not found or configuration error) && (goto three))
set /p tmp=Execution completed, press Enter to return to the menu...
cls
goto main

:four
set /p name=Please enter the task name in the parameter file
if not defined four goto four
set /p file=Please enter the parameter file path [Default: .\Temp-dataset\configs\config.yaml]:
if not defined file set file=.\Temp-dataset\configs\config.yaml
.\notion-nlp-win64.exe run-task --task-name %name% --config-file %file% || ((echo Parameter file not found or configuration error) && (goto four))
set /p tmp=Execution completed, press Enter to return to the menu...
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

