@echo off
REM Stop openmanus-mcp fleet ports
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0web_sota\stop.ps1"
if errorlevel 1 pause

