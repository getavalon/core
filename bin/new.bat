::  new.bat
::  Creation API
::
::  This file is called whenever a user creates a copy of templates, such as: new project p999_Meindbender_Sync
::
::  Arguments:
::    %1: template to copy
::    %2: name to rename the template
::
::

@echo off

if "%1"=="" goto :usage

if "%2"=="" goto :missingname

if "%1"=="project" goto :copyProject

if "%1"=="asset" goto :copyAsset

if "%1"=="shot" goto :copyAsset

if "%1"=="maya" goto :createMaya

if "%1"=="nuke" goto :createNuke

:usage
echo Enter what you want to create
goto :eof

:missingname
echo Enter the name of what you want to create
goto :eof

:copyProject
if not "%CD%"=="%PROJECTS%" goto :usage
>NUL copy %MINDBENDER_CORE%\template\ProjectName.bat .
ren ProjectName.bat %2.bat
echo new project %2 created
goto :eof

:copyAsset
if not "%CD%"=="%MINDBENDER_ROOT%\%MINDBENDER_SILO%" goto :missing
>NUL copy %MINDBENDER_CORE%\template\AssetName.bat .
>NUL ren AssetName.bat %2.bat
if "%1"=="shot" echo new shot %2 created
if "%1"=="asset" echo new Asset %2 created
goto :eof

:createMaya
if "%MINDBENDER_PROJECT%"=="" goto :missing
if "%MINDBENDER_ASSET%"=="" goto :missing
> "maya %2".bat (
echo @ECHO OFF
echo maya %2
)
mkdir %2
echo new app bat created
goto :eof

:createNuke
if "%MINDBENDER_PROJECT%"=="" goto :missing
if "%MINDBENDER_ASSET%"=="" goto :missing
> "nuke %2".bat (
echo @ECHO OFF
echo nuke %2
)
mkdir %2
echo new app bat created
goto :eof

:missing
if "%MINDBENDER_PROJECT%"=="" echo You haven't set your Project yet!
if "%MINDBENDER_ASSET%"=="" echo You haven't set your Asset or shot yet!
goto :eof
