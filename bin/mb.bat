rem :: Shell API
rem ::
rem :: This file is called whenever a user enters a shell
rem ::
rem :: Arguments:
rem :: 	 %1: Absolute path to projects directory
rem ::
rem :: Example:
rem ::   $ mb m:\projects


rem @echo off

rem if "%1"=="" goto :missing_root
rem if "%2"=="" goto :missing_pyblish

rem :: Use $ as prefix to prompt commands
rem :: The default PROMPT is the current working directory,
rem :: which can make it look a little daunting due to its length.
rem set PROMPT=$$ 

rem :: Helper variables
rem rem set BIN=%~dp0%git\pyblish-mindbender\bin

rem :: Expose executables
rem set PATH=%BIN%;%PATH%

rem :: Enable typing "mb" from a running terminal to return to square 1
rem set PATH=m:\;%PATH%

rem :: Setup environment
rem call %~dp0%_pyblish.bat

rem :: Go to projects directory
rem pushd %ROOT%

rem :: Print intro
rem echo+
rem echo  MEINDBENDER START ---------------------------
rem echo+
rem echo+
rem echo                 _,--,
rem echo              .-'---./_    __
rem echo             /o \\     '-.' /
rem echo             \  //    _.-'._\
rem echo              `"\)--"`
rem echo+
rem echo+
rem echo   Welcome %USERNAME%!
rem echo+
rem echo   1. Type application name, e.g. "maya"
rem echo   2. Press TAB to cycle through apps/projects
rem echo+
rem echo  ---------------------------------------------
rem echo+

rem :: Open a persistent shell
rem cmd.exe /K

rem goto :eof

rem :missing_root
rem    	Echo Which ROOT environment variable
