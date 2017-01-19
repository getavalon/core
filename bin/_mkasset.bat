:: Asset API
::
:: This file is called whenever a user enters an asset, such as Cat or Shot01.
::
:: Arguments:
:: 	 %1: Name of asset, e.g. Bruce
:: 	 %2: Absolute path to asset parent directory, e.g. m:\f01_projects\p999_Demo\assets
::
:: Example:
::   $ call _mkasset Bruce %~dp0

@echo off

set ASSET=%1
set ASSETDIR=%2%ASSET%

If not exist %ASSETDIR% (
	mkdir %ASSETDIR%
)

title %PROJECTDIR% / %ASSET%

:: Clear screen
cls

echo+
echo %ASSET% -----------
echo+
echo   Type application and task.
echo+
echo   For example:
echo+
echo   $ maya animation
echo   $ houdini sim
echo   $ nuke comp
echo+
echo   The following assets are allready created:
setlocal EnableDelayedExpansion
for /f %%i in ('dir %ASSETDIR%\work /b ') do (
   set x=%%i
   echo     !x!
)
echo+
echo --------------------------------------

pushd %ASSETDIR%
