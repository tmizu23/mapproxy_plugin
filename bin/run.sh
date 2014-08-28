script_dir="$(cd "$(dirname "${BASH_SOURCE:-$0}")"; pwd)"
cd $script_dir
source mypython/bin/activate
mapproxy-util serve-multiapp-develop $1
