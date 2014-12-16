script_dir="$(cd "$(dirname "${BASH_SOURCE:-$0}")"; pwd)"
cd $script_dir
source mypython/bin/activate

## set path to the numpy,scipy,opencv,mapnik ##
ln -s /usr/local/lib/python2.7/site-packages/scipy mypython/lib/python2.7/site-packages/
ln -s /usr/local/lib/python2.7/site-packages/numpy mypython/lib/python2.7/site-packages/
ln -s /Library/Python/2.7/site-packages/cv2.so mypython/lib/python2.7/site-packages/
ln -s /Library/Python/2.7/site-packages/cv.py mypython/lib/python2.7/site-packages/
ln -s /usr/local/Cellar/python/2.7.6/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/mapnik mypython/lib/python2.7/site-packages/

mapproxy-util serve-multiapp-develop $1
