MapProxy Plugin
======================
This QGIS plugin allows you to access to the tiled map images by installing MapProxy to local PC.   
By using MapProxy, the tiled map images can delivered as wms service. So QGIS will also be able to access them easily.   
MapProxy is installed by virtualenv, so your python enviroment is not polluted.  


Usage (Now testing, so please install manually)
------
1. Download source from https://github.com/tmizu23/mapproxy_plugin/archive/master.zip
2. Unzip and rename the folder to "mapproxy_plugin". Then put it to QGIS plugin directory ($HOME/.qgis2/python/plugins/) 
3. Run QGIS (>=2.0)
4. Activate MapProxy Plugin from QGIS Plugin Menu
5. Install MapProxy from QGIS Plugin Menu --> MapProxy plugin. This install needs only one time.
6. Run MapProxy server from QGIS Plugin Menu --> MapProxy plugin. If success, Layers are added.
7. Select layer you want from QGIS Plugin Menu --> MapProxy plugin


Configuring
------
You can set the layers by configuring the mapproxy yaml file. 

1. Make yaml file. Refer to http://mapproxy.org/docs/nightly/index.html
2. Put it into project directory (.qgis2/python/plugins/mapproxy_plugin/project/) 

yaml file restriction  
- Set "wms" services
- Set "srs" into "services --> wms"
- "layers --> name" is used to QGIS layer name
- "layers --> title" is used to Plugin menu's layer name

mapproxy is running by this command "mapproxy-util serve-multiapp-develop project"


LICENSE
----------
This is MIT LICENSE.
