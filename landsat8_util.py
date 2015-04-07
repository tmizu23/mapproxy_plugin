# -*- coding: utf-8 -*-
import os, sys, httplib,math
from xml.etree import ElementTree
from datetime import date
import urllib2,urllib

def check_getcapabilities(id):
   url = "http://ows8.geogrid.org/land8wms/" + id + "?request=getcapabilities&service=wms"
   response = urllib2.urlopen(url)
   data = response.read()
   if "msLoadMap" in  data:
      return False
   else:
      return True

def parse_resultXML(result,type):
   root = ElementTree.fromstring(result)
   namespace ={'ns':'http://www.w3.org/2005/Atom'}
   links = root.findall("./ns:entry/ns:published",namespace)
   date = [link.text for link in links]
   links = root.findall("./ns:entry/ns:id",namespace)
   id = [link.text for link in links]
   links = root.findall(".//opt:cloudCoverPercentage",{'opt':'http://www.opengis.net/opt/2.0'})
   cloud = [link.text for link in links]
   path = [i[3:6] for i in id]
   row = [i[6:9] for i in id]
   links = root.findall(".//georss:polygon",{'georss':"http://www.georss.org/georss"})
   pt_lon=[]
   pt_lat=[]
   for i in links:
      pt = i.text.split(' ')
      pt_lon.append([pt[0],pt[2],pt[4],pt[6]])
      pt_lat.append([pt[1],pt[3],pt[5],pt[7]])
   data=[]
   pathrow={}
   for i in range(len(id)):
      #if check_getcapabilities(id[i]):
         w = str(math.floor(min(float(pt_lon[i][0]),float(pt_lon[i][3]))))
         e = str(math.ceil(max(float(pt_lon[i][1]),float(pt_lon[i][2]))))
         n = str(math.ceil(max(float(pt_lat[i][0]),float(pt_lat[i][1]))))
         s = str(math.floor(min(float(pt_lat[i][2]),float(pt_lat[i][3]))))
         bbox = ",".join([w,s,e,n])

         pr = path[i]+","+row[i]
         if pathrow.has_key(pr):
            use='no'
            if (type=="fine" and pathrow[pr]['mincloud'] > float(cloud[i])) or ( type=="cloudy" and pathrow[pr]['mincloud'] < float(cloud[i]) ):
              data[pathrow[pr]['num']]['use']='no'
              pathrow[pr]={'num':len(data),'mincloud':float(cloud[i])}
              use='yes'
         else:
            use='yes'
            pathrow[pr]={'num':len(data),'mincloud':float(cloud[i])}

         data.append({'id':id[i],'pr':pr,'date':date[i],'cloud':cloud[i],'use':use,'bbox':bbox})
   return data
          
def makeyaml(data,output,type):
   # output sorted 'id' by 'cloud' for good order overlay
   dd = {}
   for d in data:
     if d['use']=='yes':
        dd[d['id']]=d['cloud']
   if type == 'fine':
      source_id = [key for key, value in sorted(dd.items(),key=lambda x:x[1],reverse=True)]
   else:
      source_id = [key for key, value in sorted(dd.items(),key=lambda x:x[1],reverse=False)]
   f = open(output, 'w')
   mystr = u"""services:
  demo:
  wms:
   srs: ['EPSG:4326','EPSG:3857']
   image_formats: ['image/png']
   md:
      title: Landsat8
      abstract: "Image produced and distributed by AIST, Source of Landsat 8 data: U.S. Geological Survey."
      online_resource: http://landsat8.geogrid.org/l8/index.php/ja/
      access_constraints:
            このデータは、Landsat-8直接受信・即時公開サービス(産業技術総合研究所)を利用しています。<br />
            <a href="http://landsat8.geogrid.org/l8/index.php/ja/service-3">http://landsat8.geogrid.org/l8/index.php/ja/service-3</a>
            
layers:
  - name: TITLE_TEMPLATE
    title: TITLE_TEMPLATE
    sources: [TITLE_TEMPLATE]
caches:
  TITLE_TEMPLATE:
    grids: [web]
    format: image/png
"""
   title,ext = os.path.splitext(os.path.basename(output))
   mystr = mystr.replace(u"TITLE_TEMPLATE",title)
   f.write(mystr.encode('utf_8'))
   #f.write("    sources: [" + ",".join([d['id'] for d in data if d['use']=='yes']) + "]\n")
   f.write("    sources: [" + ",".join([id for id in source_id]) + "]\n")
   f.write("sources:\n")

   for d in data:
      if d['use']=='yes':
         f.write("  "+d['id']+":\n")
         f.write("    type: wms\n")
         f.write("    req:\n")
         f.write("      url: http://ows8.geogrid.org/land8wms/" + d['id'] +"?\n")
         f.write("      layers: PANSHARPENED\n")
#         f.write("      layers: default\n")
         f.write("      transparent: true\n")
         f.write("    coverage:\n")
         f.write("      bbox: ["+ d['bbox'] +"]\n")
         f.write("      srs: 'EPSG:4326'\n")
#         f.write("    image:\n")
#         f.write("      transparent_color: '#000000'\n")
#         f.write("      transparent_color_tolerance: 30\n")

   mystr = u"""grids:
  web:
    base: GLOBAL_GEODETIC
    bbox: [122.9, 20.4, 154.0, 45.6]
    bbox_srs: EPSG:4326
"""
   f.write(mystr.encode('utf_8'))
   f.close()


def search_and_generate(type,date_start,date_end,cloud_start,cloud_end,output):
   path_start = "104"
   path_end ="116"
   row_start = "28"
   row_end = "43"

   searchURL = "http://opencsw.geogrid.org/opencsw/LANDSAT8?"
   params = "path=[" + path_start + " TO " + path_end + "]&row=[" + row_start + " TO " + row_end + "]&start=" + date_start + "T00:00:00Z&end=" + date_end + "T23:00:00Z&cloudCoverPercentage=[ " + cloud_start + " TO " + cloud_end + " ]&sort=acquisitionDate+desc&startIndex=1&count=10000&page=1"
   response = urllib2.urlopen(searchURL + urllib.quote(params,'=:+&[]'))
   result = response.read()
   data = parse_resultXML(result,type)
   #print data
   if len(data)>0:
      makeyaml(data,output,type)
   return data

def search(type,date_start,date_end,cloud_start,cloud_end,path_start,path_end,row_start,row_end):
   #path_start = "110"
   #path_end ="110"
   #row_start = "35"
   #row_end = "35"
   searchURL = "http://opencsw.geogrid.org/opencsw/LANDSAT8?"
   params = "path=[" + path_start + " TO " + path_end + "]&row=[" + row_start + " TO " + row_end + "]&start=" + date_start + "T00:00:00Z&end=" + date_end + "T23:00:00Z&cloudCoverPercentage=[ " + cloud_start + " TO " + cloud_end + " ]&sort=acquisitionDate+desc&startIndex=1&count=10000&page=1"
   response = urllib2.urlopen(searchURL + urllib.quote(params,'=:+&[]'))
   result = response.read()
   data = parse_resultXML(result,type)
   return data

if __name__ == "__main__":
   search_and_generate("fine","2014-01-01","2014-12-31","0","100","landsat8.yaml")