:: :: Following is the commands that needs to be called in the bat
:: :: always call _mkproject
:: %~n0 is the name of this project as the name of the .bat
:: %~dp0 is drive plus path variable
@echo off
call _mkasset %~n0 %~dp0%

:: :: Following is the variables that can be set in the bat
:: :: They are default set to "nothing"
:: :: leave them be if you dont have the info for them and return to them later.
set OBJECT3D=
Set MINDBENDER_EDIT_IN=
Set MINDBENDER_EDIT_OUT=