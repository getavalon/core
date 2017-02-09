:: Following is the commands that needs to be called in the bat
:: call _mkasset
:: %~n0 is the name of this project as the name of the .bat
:: %~dp0 is drive plus path variable
@echo off
call _mkasset %~n0 %~dp0%

:: Following is the variables that can be set in the bat
:: They are default set to "nothing"
:: leave them be if you dont have the info for them and return to them later.
:: setOBJECT expects a string like "prop, char"
:: MINDBENDER_EDIT_IN and MINDBENDER_EDIT_OUT sets the assets time in and out for the edit. 
:: These should not be set for assets, use this options for shots
set OBJECT3D=
set MINDBENDER_EDIT_IN=
set MINDBENDER_EDIT_OUT=