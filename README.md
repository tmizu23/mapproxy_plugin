MapProxy Plugin
======================
GeoTiffをUTFGridに変換するプログラムです。  
試しに作ってみました。

作成例
------
標高の例  
http://www.ecoris.co.jp/map/utfgrid_test.html?zoom=13&lat=4823548.9824&lon=15744694.52498&layers=BTTTTTT

植生の例  
http://www.ecoris.co.jp/map/utfgrid_test.html?zoom=13&lat=4799872.6129&lon=15744694.52498&layers=BTTTTTT

絵地図の例  
http://www.ecoris.co.jp/map/utfgrid_test.html?zoom=16&lat=4607129.48013&lon=15683405.16591&layers=BTTTTTT

プログラム
------
- `gdal2tilesXYZ1band.py`  
 1バンドのGeoTIFFを1バンドのXYZタイルに変換します。gdal2tilesは強制的に3バンドに変換するので、1バンドのデータをそのまま1バンドのままタイルにします。また、その際にTMS形式ではなくXYZ形式で出力します。
- `gdal2tilesXYZ.py`  
 3バンドのGeoTIFFを3バンドのXYZタイルに変換します。gdal2tilesの出力はTMS形式なので、それをXYZ形式にしたものです。ただし、gdal2tilesが出力するメタデータやhtmlは出力しません。
- `tile2utfgrid.py`  
 タイル画像からUTFGridファイル(.json)を作成します。
- `tile2utfgrid.bat`  
 OSGeo4Wのためのファイルです。上記プログラムを呼び出すだけです。
- `gdal2tilesXYZ1band.bat`  
 OSGeo4Wのためのファイルです。上記プログラムを呼び出すだけです。
- `gdal2tilesXYZ.bat`  
 OSGeo4Wのためのファイルです。上記プログラムを呼び出すだけです。

 
関連情報
--------
[https://github.com/mapbox/utfgrid-spec/blob/master/1.2/utfgrid.md](https://github.com/mapbox/utfgrid-spec/blob/master/1.2/utfgrid.md "utfgrid.md")  
[http://d.hatena.ne.jp/tmizu23/20121107](http://d.hatena.ne.jp/tmizu23/20121107)

  
ライセンス
----------
考え中
