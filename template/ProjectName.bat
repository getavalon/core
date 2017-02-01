:: :: Following is the commands that needs to be called in the bat
:: :: always call _mkproject
:: %~dp0 is drive plus path variable
:: %~n0 is the name of this project as the name of the .bat
:: \\f02_prod is the folder that you will be
:: %1 is the entry by the user for asset
@echo off
call _mkproject %~dp0 %~n0 \\f02_prod %1

:: :: Following is the variables that can be set in the bat
:: :: They are default set to "nothing"
:: :: leave them be if you dont have the info for them and return to them later.
set MINDBENDER_SETASSETCATEGORY=
set MINDBENDER_ASSETCATEGORY=
set MINDBENDER_FPS=
set MINDBENDER_RESOLUTION_WIDTH=
set MINDBENDER_RESOLUTION_HEIGHT=