script_dir="$(cd "$(dirname "${BASH_SOURCE:-$0}")"; pwd)"
cd $script_dir
python virturlenv.py mypython
source mypython/bin/activate
pip install pillow
pip install https://github.com/mapproxy/mapproxy/tarball/master
cp fonts/message.py mypython/lib/python2.7/site-packages/mapproxy/image/
cp fonts/ipaexg.ttf mypython/lib/python2.7/site-packages/mapproxy/image/fonts/
