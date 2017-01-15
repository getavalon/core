:: Project API
::
:: This file is called whenever a user enters a project, such p999_Meindbender_Sync
::
:: Arguments:
:: 	 %1: Absolute path to project
:: 	 %2: Subdirectory, e.g. asset or film
::
:: Variables:
::   %PROJECTDIR%: Absolute path to project directory
::
:: Example:
::   $ call _mkproject.bat %~dp0ProjectName assets

@echo off

if "%1"=="" goto :missing_project
if "%2"=="" goto :missing_subdirectory

set PROJECTDIR=%1

if not exist %PROJECTDIR% (
	echo Creating new project "%PROJECT%"..

	mkdir %PROJECTDIR%\assets
	mkdir %PROJECTDIR%\film
	rem etc..
)

pushd %PROJECTDIR%\%2


echo+
echo  ASSETS -----------
echo+

:: List available assets, without their .bat suffix
setlocal enabledelayedexpansion
for %%i in (*.bat) do (
    set temp=%%i
    echo   !temp:.bat=!
)

echo+
echo   1. Type first letters of asset
echo   2. Press [TAB] to auto-complete
echo+
echo  --------------------------------------

goto :eof

:missing_project
   	echo ERROR: Missing FULLPATH
:missing_subdirectory
    echo ERROR: Missing SUBFOLDER

echo+
echo Syntax: _mkproject FULLPATH SUBFOLDER
