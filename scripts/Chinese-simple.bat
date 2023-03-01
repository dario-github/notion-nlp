@echo off

color 0a
:: �״�ִ�нű���������Դ�ļ�
if not exist ".\Temp-dataset\configs\config.yaml" (
    echo ��⵽�ű��״�ִ�У���������Դ�ļ���ִ�������������ĵȴ� 1-3 min...
    .\notion-nlp-win64.exe first-try
    IF NOT %ERRORLEVEL% EQU 0 (
      echo "����δ֪����...���������ߴ������ǵø�������Ĵ�����־Ŷ~������ճ����־ ==> https://reurl.cc/b7nDkl"
      set /p tmp=�밴������˳��ű�...
      exit)
    echo ����������ִ����ϣ��밴�س����鿴����ͼ������Ŀ¼
    set /p tmp=�鿴����Ч�����뷵�ر����ڣ�������һ����...
::    start "" ".\Temp-dataset\results\wordcloud\chinese-simple_task\colormap_viridis.png"
    start "" ".\Temp-dataset\results\wordcloud\chinese-simple_task"
    echo=
    set /p tmp=�밴�س����鿴�����ܽ�markdown�ĵ�...
    start "" ".\Temp-dataset\results\tfidf_analysis\chinese-simple_task\chinese-simple_task.top_5.md"
    echo=
    echo "��������Լ������񣿽̳�ָ�� ==> https://github.com/dario-github/notion-nlp/blob/main/README.zh.md#%E4%BD%BF%E7%94%A8"
    echo=
    set /p tmp=�밴�س����򿪲����ļ�����ʼ�������Լ�������...
    copy /y ".\Temp-dataset\configs\config.test.yaml" ".\Temp-dataset\configs\config.yaml" > nul
    start "" ".\Temp-dataset\configs\config.yaml"
    echo=
    echo /p tmp=�밴�س����������˵�...
    cls
) else (
    echo=
)

color 0a
:main
color 0a

echo ================== �� Notion ��Ȼ���Դ��� �� ======================
echo=
echo ����:  Dario Zhang
echo �汾:  v1.0.7.2
echo ����:  https://github.com/dario-github/notion-nlp
echo ����:  ��Notion���ݿ��ж�ȡ�ı���������Ȼ���Դ�������
echo=
echo =========================   �ƹ���   ============================
echo=                                   
echo ��������:  https://reurl.cc/7R3MeN
echo=
echo ==============================================================
echo=
echo 1. �鿴������Ϣ
echo 2. ������������
echo 3. ����ָ������
echo 4. ������������

echo=
set /p opt=ѡ�� (�������):

if %opt% == 1 goto one
if %opt% == 2 goto two
if %opt% == 3 goto three
if %opt% == 4 goto lastopt

echo ��Чѡ��
cls
goto main

:: �鿴������Ϣ
:one
.\notion-nlp-win64.exe task-info --config-file ".\Temp-dataset\configs\config.yaml"
IF %ERRORLEVEL% EQU 0 GOTO endresult
echo δ�ҵ������ļ������ô����밴�ս̳̼�������ļ�
goto main

:: ִ����������
:two
.\notion-nlp-win64.exe run-all-tasks --config-file ".\Temp-dataset\configs\config.yaml"
IF %ERRORLEVEL% EQU 0 GOTO endresult
echo δ�ҵ������ļ������ô����밴�ս̳̼�������ļ�
goto main

:: ִ�е�������
:three
set /p name=����������ļ��е���������������ո�����˫���Ű��������������� info �鿴����������Ϣ: 
if not defined name goto three
if %name% == info goto one
.\notion-nlp-win64.exe run-task --task-name %name% --config-file ".\Temp-dataset\configs\config.yaml"
IF %ERRORLEVEL% EQU 0 GOTO endresult
echo δ�ҵ������ļ������ô����밴�ս̳̼�������ļ�
goto main


:endresult
echo=
echo  �������������[ �����[  �����[
echo �����X�T�T�T�����[�����U �����T�a
echo �����U   �����U���������U
echo �����U   �����U�����U �����[
echo �^�������������X�a�����U�[ �����[
echo  �^�T�T�T�T�T�a �^�T�T�a �^�T�a
echo=
set /p tmp=ִ����ϣ��밴�س������ز˵�...
cls
goto main


:lastopt
start parrot.bat
goto main