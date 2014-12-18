script_dir="$(cd "$(dirname "${BASH_SOURCE:-$0}")"; pwd)"
cd $script_dir
python virturlenv.py mypython
#home brew python
#/usr/local/bin/python virturlenv.py mypython
source mypython/bin/activate
pip install https://github.com/tmizu23/mapproxy/tarball/geojson