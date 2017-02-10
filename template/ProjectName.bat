:: Following is the commands that needs to be called in the bat
::
:: call _mkproject
:: %~dp0 is drive plus path variable
:: %~n0 is the name of this project as the name of the .bat
:: %1 is the entry by the user for asset
@echo off
call _mkproject %~dp0 %~n0 %1

:: Following is the variables that can be set in the bat
::
set MINDBENDER_ASSETCATEGORY=
set MINDBENDER_FPS=
set MINDBENDER_RESOLUTION_WIDTH=
set MINDBENDER_RESOLUTION_HEIGHT=