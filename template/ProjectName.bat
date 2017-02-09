:: Following is the commands that needs to be called in the bat
:: call _mkproject
:: %~dp0 is drive plus path variable
:: %~n0 is the name of this project as the name of the .bat
:: %1 is the entry by the user for asset
@echo off
call _mkproject %~dp0 %~n0 %1

:: Following is the variables that can be set in the bat
:: They are default set to "nothing"
:: leave them be if you dont have the info for them and return to them later.
:: MINDBENDER_SETASSETCATEGORY should always be set to nothing, this is a reset
:: MINDBENDER_ASSETCATEGORY expects categorys split by a "," exampel "prop, env, char"
:: MINDBENDER_FPS, MINDBENDER_RESOLUTION_WIDTH, MINDBENDER_RESOLUTION_HEIGHT expects a 
:: number value without letter characters
set MINDBENDER_SETASSETCATEGORY=
set MINDBENDER_ASSETCATEGORY=
set MINDBENDER_FPS=
set MINDBENDER_RESOLUTION_WIDTH=
set MINDBENDER_RESOLUTION_HEIGHT=