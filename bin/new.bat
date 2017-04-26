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

if "%2"=="" goto :missing_name

if "%1"=="project" goto :copy_project

if "%1"=="asset" goto :copy_asset

if "%1"=="shot" goto :copy_asset

if "%1"=="maya" goto :create_maya

if "%1"=="nuke" goto :create_nuke

:usage
echo You need to enter two arguments.
echo Example: "new maya animation"
goto :eof

:missing_name
echo Enter the name of what you want to create
goto :eof

:copy_project
if not "%CD%"=="%PROJECTS%" goto :usage
>NUL copy %MINDBENDER_CORE%\template\ProjectName.bat .
ren ProjectName.bat %2.bat
echo new project %2 created
goto :eof

:copy_asset
if not "%CD%"=="%MINDBENDER_PROJECTPATH%\%MINDBENDER_SILO%" goto :missing
>NUL copy %MINDBENDER_CORE%\template\AssetName.bat .
>NUL ren AssetName.bat %2.bat
if "%1"=="shot" echo new shot %2 created
if "%1"=="asset" echo new asset %2 created
goto :eof

:create_maya
if "%MINDBENDER_PROJECT%"=="" goto :missing
if "%MINDBENDER_ASSET%"=="" goto :missing
> "maya %2".bat (
echo @ECHO OFF
echo maya %2
)
mkdir %2
echo new app bat created
goto :eof

:create_nuke
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
