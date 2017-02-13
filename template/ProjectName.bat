:: Following is the commands that needs to be called in the bat
::
:: call _mkproject
:: %~dp0 is drive plus path variable
:: %~n0 is the name of this project as the name of the .bat
:: %1 is the entry by the user for asset
@echo off
call _mkproject %~dp0 %~n0 %1

:: --------------------
:: Additional Variables
:: --------------------

:: (int): Current frames per second for the project
set MINDBENDER_FPS=25

:: (str): Render resolution width
set MINDBENDER_RESOLUTION_WIDTH=1920

:: (str): Render resolution height
set MINDBENDER_RESOLUTION_HEIGHT=1080
