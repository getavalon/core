:: %~dp0 is drive plus path variable
:: %~n0 is the name of this project as the name of the .bat
:: %1 is the entry by the user for asset

@echo off
call _mkproject %~dp0 %~n0 %1