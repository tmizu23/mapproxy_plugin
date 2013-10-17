cd /d %~dp0
python virturlenv.py mypython
call mypython\Scripts\activate.bat
easy_install pillow
pip install https://github.com/mapproxy/mapproxy/tarball/master
copy /Y ..\project\cjp_src\tile.py mypython\lib\site-packages\mapproxy\client\
copy /Y ..\project\cjp_src\message.py mypython\lib\site-packages\mapproxy\image\
copy /Y ..\project\cjp_src\ipaexg.ttf mypython\lib\site-packages\mapproxy\image\fonts\