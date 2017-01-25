:: Extra Step Terminal API
::
:: This file is called whenever a user enters an asset, such as Cat or Shot01.
::
:: Arguments:
::   %1: Name of bat and also the step
::   %2: Absolute path to parent directory, e.g. m:\f01_projects\p999_Demo\assets
::   %3: function to be called e.g. 
::   %4: 
::
:: Example:
::   $ call _mkextrastep %~n0 %~dp0 function MINDBENDER_CATEGORY

 @echo off

:: Usage Dependencies
If "%1"=="" goto :usage
If "%2"=="" goto :usage
If "%3"=="" goto :usage

:: Extra Dependencies
IF "%PROJECTS%"=="" goto :missing

:: Variable assining
SET EXTRASTEP=%1
SET FUNCTION=%3

title Mindbender Launcher - %PROJECTS% - %EXTRASTEP%

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
