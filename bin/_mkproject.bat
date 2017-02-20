::  Project API
::
::  This file is called whenever a user enters a project, such p999_Meindbender_Sync
::
::  Arguments:
::    %1: Path = Absolute path to projects
:: 	  %2: Name = Name of project
::    %3: Silo = Parent directory name of assets
::
::  Variables set by bat:
::    %MINDBENDER_FPS%: Is the project FPS 
::    %MINDBENDER_RESOLUTION_WIDTH%: Is the project width
::    %MINDBENDER_RESOLUTION_HEIGHT%: Is the project height
::
::  Variables:
::    %MINDBENDER_PROJECTPATH%: Absolute path to project directory
::
::  Example:
::    $ call _mkproject.bat %~dp0ProjectName assets
::    $ set MINDBENDER_FPS=24

@echo off

if "%1"=="" goto :missing_projectdir
if not "%3"=="assets" (
  if not "%3"=="film" goto :missing_silo
)

if "%2"=="" goto :missing_name
if "%3"=="" goto :missing_silo

set MINDBENDER_PROJECT=%2
set MINDBENDER_PROJECTPATH=%1%2

if not exist %MINDBENDER_PROJECTPATH% (
  echo Creating new project "%MINDBENDER_PROJECTPATH%"..

  mkdir %MINDBENDER_PROJECTPATH%\assets
  mkdir %MINDBENDER_PROJECTPATH%\film
  rem etc..
)

:: Establish base directories for ls() and search() functions.
set MINDBENDER_ROOT=%MINDBENDER_PROJECTPATH%
set MINDBENDER_SILO=%3

pushd %MINDBENDER_PROJECTPATH%\%MINDBENDER_SILO%

:: Clear screen
cls

echo+
echo    Active Project: %MINDBENDER_PROJECT%
echo    You are in: %MINDBENDER_SILO%
echo+

:: List available assets, without their .bat suffix
setlocal enabledelayedexpansion
for %%i in (*.bat) do (
    set temp=%%i
    echo   !temp:.bat=!
)
endlocal

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
:missing_silo
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
