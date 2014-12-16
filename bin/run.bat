cd /d %~dp0
call mypython\Scripts\activate.bat
REM ベクトルタイル用(mapnik)
set PATH=C:\mapnik-v2.2.0\lib;c:\\mapnik-v2.2.0\bin;%PATH%
set PYTHONPATH=C:\mapnik-v2.2.0\python\2.7\site-packages;%PYTHONPATH%
start "mapproxy server"/min mapproxy-util serve-multiapp-develop %1
