:: Terminal API
::
:: This file is called whenever a user enters a shell.
::
:: Dependencies:
::  - pyblish-base
::  - pyblish-maya
::  - pyblish-nuke
::  - pyblish-houdini
::  - pyblish-lite
::  - pyblish-qml
::  - pyblish-mindbender
::
:: Usage:
:: 	1. Create a local `mb.bat` file and set the required environment variables
::  2. Call your `mb.bat`
::
:: Example:
::   $ mb

@echo off

if "%1"=="" goto :usage

:: External Dependencies
if "%PYBLISH_BASE%"=="" goto :missing
if "%PYBLISH_MAYA%"=="" goto :missing
if "%PYBLISH_NUKE%"=="" goto :missing
if "%PYBLISH_LITE%"=="" goto :missing
if "%PYBLISH_QML%"=="" goto :missing
if "%PYBLISH_MINDBENDER%"=="" goto :missing

set PYTHONPATH=%PYBLISH_BASE%;%PYTHONPATH%
set PYTHONPATH=%PYBLISH_MAYA%;%PYTHONPATH%
set PYTHONPATH=%PYBLISH_NUKE%;%PYTHONPATH%
set PYTHONPATH=%PYBLISH_LITE%;%PYTHONPATH%
set PYTHONPATH=%PYBLISH_QML%;%PYTHONPATH%
set PYTHONPATH=%PYBLISH_MINDBENDER%;%PYTHONPATH%

set PROJECTS=%1

:: Expose pipeline executables
set PATH=%PYBLISH_MINDBENDER%\bin;%PATH%

:: --------------------
:: User interface
:: --------------------

:: Use $ as prefix to prompt commands
:: The default PROMPT is the current working directory,
:: which can make it look a little daunting due to its length.
set PROMPT=$$ 

:: Go to projects directory
pushd %PROJECTS%

:: Clear screen
title Mindbender Pipeline
cls

:: Print intro
echo+
echo  MEINDBENDER START ---------------------------
echo+
echo+
echo                 _,--,
echo              .-'---./_    __
echo             /o \\     '-.' /
echo             \  //    _.-'._\
echo              `"\)--"`
echo+
echo+
echo   Welcome %USERNAME%!
echo+
echo   1. Type first characters of a project, e.g. "p999_"
echo   2. Press TAB to cycle through matching projects
echo+
echo  ---------------------------------------------
echo+

:: Clearing old Variables
SET PROJECTDIR=
SET ASSET=

:: Open a persistent shell
cmd.exe /K

goto :eof

:usage
	echo Not enough arguments
	echo Example: mb.bat c:\path\to\projects

:missing
	echo ERROR: Missing environment variables.
	if "%PYBLISH_BASE%"=="" echo   - %%PYBLISH_BASE%%
	if "%PYBLISH_MAYA%"=="" echo   - %%PYBLISH_MAYA%%
	if "%PYBLISH_NUKE%"=="" echo   - %%PYBLISH_NUKE%%
	if "%PYBLISH_LITE%"=="" echo   - %%PYBLISH_LITE%%
	if "%PYBLISH_QML%"=="" echo   - %%PYBLISH_QML%%
	if "%PYBLISH_MINDBENDER%"=="" echo   - %%PYBLISH_MINDBENDER%%

	exit /b