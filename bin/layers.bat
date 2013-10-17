@echo off
cd /d %~dp0
call mypython\Scripts\activate.bat
python layers.py %1
