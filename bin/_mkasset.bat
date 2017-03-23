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

set MINDBENDER_ASSET=%1
set MINDBENDER_ASSETPATH=%2%MINDBENDER_ASSET%

If not exist %MINDBENDER_ASSETPATH% (
	mkdir %MINDBENDER_ASSETPATH%
	mkdir %MINDBENDER_ASSETPATH%\work
)

title %MINDBENDER_PROJECTPATH% / %MINDBENDER_ASSET%

:: Clear screen
cls

echo+
echo    %MINDBENDER_ASSET% -----------
echo+
echo+
echo    1. Type application and task.
echo    2. Press [Enter] to launch application.
echo+
echo    For example:
echo+
echo    $ maya animation
echo    $ nuke comp
echo+

:: List available tasks, without their .bat suffix
setlocal enabledelayedexpansion
set FOLDERQUERY=%MINDBENDER_ASSETPATH%\work
if exist %FOLDERQUERY%\*.bat (
	echo   These are available:
	for /r %FOLDERQUERY%\. %%g in (*.bat) do (
		set temp=%%~nxg
    	echo    $ !temp:.bat=!
	)
)
endlocal


echo+
echo --------------------------------------

pushd %MINDBENDER_ASSETPATH%\work
