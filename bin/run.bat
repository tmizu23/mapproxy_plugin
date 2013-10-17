cd /d %~dp0
call mypython\Scripts\activate.bat
start "mapproxy server"/min mapproxy-util serve-multiapp-develop %1
