:: Terminal API
::
:: This file is called whenever a user enters a shell.
::
:: Dependencies:
::   mb.bat add following = set PATH=%_GIT%\mindbender-core\bin\back\;%PATH%
::
:: Example:
::   $ mb

@echo off

::IF %CD%
IF "%PROJECTDIR%"=="" goto :return_to_mb

IF "%ASSET%"=="" goto :return_to_mb

IF NOT "%ASSET%"=="" goto :return_to_projects
:return_to_mb
    call %_MB% M:\f01_projects %*
    SET PROJECTDIR=
    exit /b
:return_to_projects
    call _mkproject.bat %curPROJECT% %curPROJECTNAME% %PROJECTSTAGE%
    SET ASSET=
    exit /b
