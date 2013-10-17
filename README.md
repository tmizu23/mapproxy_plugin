MapProxy Plugin
======================
This QGIS plugin allows you to access to the tiled map images by installing MapProxy to local PC.   
By using MapProxy, the tiled map images can delivered as wms service. So QGIS will also be able to access them easily.   
MapProxy is installed by virtualenv, so your python enviroment is not polluted.  


Usage
------
1. Run QGIS (>=2.0)
2. Activate MapProxy Plugin from QGIS Plugin Menu
3. Install MapProxy from QGIS Plugin Menu --> MapProxy plugin. This install needs only one time.
4. Run MapProxy server from QGIS Plugin Menu --> MapProxy plugin. If success, Layers are added.
5. Select layer you want from QGIS Plugin Menu --> MapProxy plugin


Configuring
------
You can set the layers by configuring the mapproxy yaml file.  

1. make yaml file. Refer to http://mapproxy.org/docs/nightly/index.html
2. put it into project directory (.qgis2/python/plugins/mapproxy_plugin/project/) 

yaml file restriction  
- set "wms" services
- set "srs" into services --> wms


LICENSE
----------
This is MIT LICENSE.
