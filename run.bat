@echo off
cd /d %~dp0
echo ===============================
echo Starting Project Launcher...
echo ===============================

::  Launcher.pyを実行する
echo Launching the UI...
echo ===============================
echo Launcher has been started!
echo ===============================
python docker_launcher.py

pause
