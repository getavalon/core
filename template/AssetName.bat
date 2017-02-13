:: Following is the commands that needs to be called in the bat
::
:: call _mkasset
:: %~n0 is the name of this project as the name of the .bat
:: %~dp0 is drive plus path variable
@echo off
call _mkasset %~n0 %~dp0%

:: ------------------
:: Additional variables
:: ------------------

:: (str, optional): This variable is ??????, for example "prop, char"
set MINDBENDER_OBJECT3D=

:: (int, optional): In-time used in the edit
set MINDBENDER_EDIT_IN=101

:: (int, optional): Out-time used in the edit
set MINDBENDER_EDIT_OUT=201
