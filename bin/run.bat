cd /d %~dp0
call mypython\Scripts\activate.bat

REM ベクトルタイル用設定(mapnik)
REM mapnikをインストールしたフォルダを指定してください
set MAPNIK_HOME=C:\mapnik-v2.2.0

set PATH=%MAPNIK_HOME%\lib;%MAPNIK_HOME%\bin;%PATH%
set PYTHONPATH=%MAPNIK_HOME%\python\2.7\site-packages;%PYTHONPATH%

start "mapproxy server"/min mapproxy-util serve-multiapp-develop %1
