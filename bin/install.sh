script_dir="$(cd "$(dirname "${BASH_SOURCE:-$0}")"; pwd)"
cd $script_dir
python virturlenv.py mypython
source mypython/bin/activate
pip install pillow
pip install https://github.com/mapproxy/mapproxy/tarball/master
