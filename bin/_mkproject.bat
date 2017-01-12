:: Project API
::
:: This file is called whenever a user enters a project, such p999_Meindbender_Sync
::
:: Arguments:
:: 	 %1: Absolute path to project
:: 	 %2: Subdirectory, e.g. asset or film
::
:: Variables:
::   %PROJECT%: Basename of project directory, e.g. p999_Meindbender_Sync
::   %PROJECTDIR%: Absolute path to project directory
::
:: Example:
::   $ p999_Meindbender_Sync

@echo off

set PROJECTDIR=%1

:: Use basename of path as project name, e.g. "p999_Meindbender_Sync"
for /F %%i in ("%1") do @set PROJECT=%%~nxi

if Not exist %PROJECTDIR% (
	echo Creating new project "%PROJECT%"..

	mkdir %PROJECTDIR%\assets
	mkdir %PROJECTDIR%\film
	rem etc..
)

echo+
echo %PROJECT% -----------
echo+
echo   1. Type first letters of asset
echo   2. Press [TAB] to auto-complete
echo+
echo   For example:
echo+
echo   $ sh01
echo   $ Fiona
echo   $ CatFish
echo+
echo --------------------------------------

pushd %PROJECTDIR%\%2
