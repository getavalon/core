:: Assets Category API
::
:: This file is called whenever a user enters an asset, such as Cat or Shot01.
::
:: Arguments:
::   %1: Name of asset, e.g. Bruce
::   %2: Absolute path to asset parent directory, e.g. m:\f01_projects\p999_Demo\assets
::
:: Example:
::   $ call _mkasset Bruce %~dp0

@echo off

If "%ASSETSCATE%"=="" goto :missing

title %PROJECTDIR% / %ASSETSCATE%

cd %ASSETSCATE%

:: Clear screen
cls

echo+
echo    Active Project: %PROJECTNAME%
echo    You are in: %ASSETSCATE% -------
echo+

:: List available assets, without their .bat suffix
setlocal enabledelayedexpansion
for %%i in (*.bat) do (
    set temp=%%i
    echo   !temp:.bat=!
)
endlocal


echo+
echo   1. Type first letters of asset category
echo   2. Press [TAB] to auto-complete
echo+
echo  --------------------------------------

goto :eof

:missing
    echo ERROR: Missing FULLPATH
    exit /b
