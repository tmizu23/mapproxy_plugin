cd /d %~dp0
call mypython\Scripts\activate.bat
REM �x�N�g���^�C���p(mapnik)
set PATH=c:\\mapnik-v2.2.0\lib;c:\\mapnik-v2.2.0\bin;%PATH%
set PYTHONPATH=c:\\mapnik-v2.2.0\python\2.7\site-packages;%PYTHONPATH%
REM �W���^�C���p(numpy,scipy)
set PYTHONPATH=C:\\OSGeo4W\apps\Python27\Lib\site-packages;%PYTHONPATH%
REM OpenCV�p(cv2)
set PYTHONPATH=C:\\OSGeo4W\apps\Python27\Lib\site-packages;%PYTHONPATH%
start "mapproxy server"/min mapproxy-util serve-multiapp-develop %1
