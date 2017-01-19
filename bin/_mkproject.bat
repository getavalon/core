:: Project API
::
:: This file is called whenever a user enters a project, such p999_Meindbender_Sync
::
:: Arguments:
::   %1: Path: Absolute path to projects
:: 	 %2: Name: Name of project
:: 	 %3: Stage: assets or film
::
:: Variables:
::   %PROJECTDIR%: Absolute path to project directory
::
:: Example:
::   $ call _mkproject.bat %~dp0ProjectName assets

@echo off

if "%1"=="" goto :missing_projectdir
if not "%3"=="assets" (
  if not "%3"=="film" goto :missing_stage
)

if "%2"=="" goto :missing_name
if "%3"=="" goto :missing_stage

set PROJECTDIR=%1%2
set curPROJECT=%1
set curPROJECTNAME=%2
set PROJECTSTAGE=%3

if not exist %PROJECTDIR% (
	echo Creating new project "%PROJECT%"..

	mkdir %PROJECTDIR%\assets
	mkdir %PROJECTDIR%\film
	rem etc..
)

:: Establish base directory for ls() and search() functions.
set PYBLISHMINDBENDERROOT=%PROJECTDIR%

pushd %PROJECTDIR%\%3

:: Clear screen
cls

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

:missing_name
   	echo ERROR: Missing FULLPATH
   	exit /b
:missing_projectdir
	exit /b
:missing_stage
    echo  Uh oh..
    echo    Specify either "assets" or "film"
    echo+
    echo  Example:
    set temp=%2
    echo    $ %temp% assets
    echo    $ %temp% film
    exit /b

echo+
echo Syntax: _mkproject FULLPATH SUBFOLDER
