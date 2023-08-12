@echo off
setlocal

REM Detect current working path
set CurrDir=%cd%

REM Execute the python script
python.exe C:\Projekte\PromptExecute\main.py %CurrDir%

endlocal
