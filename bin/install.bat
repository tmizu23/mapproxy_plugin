cd /d %~dp0
python virturlenv.py --system-site-packages mypython
call mypython\Scripts\activate.bat
pip install https://github.com/tmizu23/mapproxy/tarball/geojson
