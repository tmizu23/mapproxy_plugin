cd /d %~dp0
python virturlenv.py mypython
call mypython\Scripts\activate.bat
easy_install pillow
pip install https://github.com/mapproxy/mapproxy/tarball/master
