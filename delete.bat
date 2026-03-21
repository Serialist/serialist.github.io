@echo off
setlocal enabledelayedexpansion

:: Define target paths (NO SPACES around = sign!)
set "target_dir=./page/blog/"
set "keep_file=index.md"
set "delete_json=articles.json"

:: 1. Check if target directory exists
if not exist "%target_dir%" (
    echo Error: Blog directory "%target_dir%" does not exist!
    pause
    exit /b 1
)

:: 2. Delete all files except index.md in target directory
echo Deleting all files in "%target_dir%" except %keep_file%...
for %%f in ("%target_dir%\*.*") do (
    :: Skip the file we want to keep (case-insensitive)
    if /i not "%%~nxf"=="%keep_file%" (
        del /f /q "%%f" >nul 2>&1
        if !errorlevel! equ 0 (
            echo Deleted: %%~nxf
        ) else (
            echo Error deleting: %%~nxf
        )
    )
)

:: 3. Delete articles.json file
echo.
echo Deleting %delete_json%...
if exist "%delete_json%" (
    del /f /q "%delete_json%" >nul 2>&1
    if !errorlevel! equ 0 (
        echo Deleted: %delete_json%
    ) else (
        echo Error deleting: %delete_json% (permission denied or file locked)
    )
) else (
    echo Attention: %delete_json% does not exist!
)

echo.
echo Execution completed!
pause
endlocal