@echo off
setlocal enableextensions disabledelayedexpansion

:: Echo all variables starting with 'MINDBENDER_'
for /f "tokens=1,* delims==" %%a in ('set MINDBENDER_') do (
	echo %%a = %%b
)
