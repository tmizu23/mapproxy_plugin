# -*- coding: utf-8 -*-
import os, sys, httplib,math
from xml.etree import ElementTree
from datetime import date
import urllib2

def generate_search_xml(date_start,date_end,cloud_start,cloud_end,path_start,path_end,row_start,row_end):
   f = open(os.path.dirname(__file__) + os.sep + 'search_template.xml', 'r')
   template = f.read()
   xmltext = template.replace("date_start",date_start).replace("date_end",date_end).replace("cloud_start",cloud_start).replace("cloud_end",cloud_end).replace("path_start",path_start).replace("path_end",path_end).replace("row_start",row_start).replace("row_end",row_end)
   f.close()
   return xmltext

def do_request(request):
   """HTTP XML Post request, by www.forceflow.be"""
   HOST = "csw2.geogrid.org"
   API_URL = "/CSW/opensat"
   webservice = httplib.HTTP(HOST)
   webservice.putrequest("POST", API_URL)
   webservice.putheader("Host", HOST)
   webservice.putheader("User-Agent","Python post")
   webservice.putheader("Content-type", "text/xml; charset=\"UTF-8\"")
   webservice.putheader("Content-length", "%d" % len(request))
   webservice.endheaders()
   webservice.send(request)
   statuscode, statusmessage, header = webservice.getreply()
   result = webservice.getfile().read()
   print statuscode, statusmessage, header
   return result

def check_getcapabilities(id):
   url = "http://ows.geogrid.org/land8wms/" + id + "?request=getcapabilities&service=wms"
   response = urllib2.urlopen(url)
   data = response.read()
   if "msLoadMap" in  data:
      return False
   else:
      return True

def parse_resultXML(result,type):
   root = ElementTree.fromstring(result)
   namespace ={'rim':'urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0'}
   namespace2 ={'gml':'http://www.opengis.net/gml'}

   links = root.findall(".//*[@name='urn:ogc:def:slot:OGC-CSW-ebRIM-EO::acquisitionDate']",namespace)
   date = [link[0][0].text for link in links]
   links = root.findall(".//*[@objectType='urn:ogc:def:objectType:OGC-CSW-ebRIM-EO::EOBrowseInformation']/*[@name='urn:ogc:def:slot:OGC-CSW-ebRIM-EO::fileName']",namespace)
   id = [link[0][0].text.split("/")[4].split("?")[0] for link in links]
   links = root.findall(".//*[@name='urn:ogc:def:slot:OGC-CSW-ebRIM-EO::cloudCoverPercentage']",namespace)
   cloud = [link[0][0].text for link in links]
   links = root.findall(".//*[@name='urn:ogc:def:slot:OGC-CSW-ebRIM-EO::wrsLongitudeGrid']",namespace)
   path = [link[0][0].text for link in links]
   links = root.findall(".//*[@name='urn:ogc:def:slot:OGC-CSW-ebRIM-EO::wrsLatitudeGrid']",namespace)
   row = [link[0][0].text for link in links]
   links = root.findall(".//gml:LinearRing",namespace2)
   p1 = [link[0].text.split(' ') for link in links]
   p2 = [link[1].text.split(' ') for link in links]
   p3 = [link[2].text.split(' ') for link in links]
   p4 = [link[3].text.split(' ') for link in links]

   data=[]
   pathrow={}
   for i in range(len(id)):
      if check_getcapabilities(id[i]):
         w = str(math.floor(min(float(p1[i][0]),float(p4[i][0]))))
         e = str(math.ceil(max(float(p2[i][0]),float(p3[i][0]))))
         n = str(math.ceil(max(float(p1[i][1]),float(p2[i][1]))))
         s = str(math.floor(min(float(p3[i][1]),float(p4[i][1]))))
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
         f.write("      url: http://ows.geogrid.org/land8wms/" + d['id'] +"?\n")
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

   xmltext = generate_search_xml(date_start,date_end,cloud_start,cloud_end,path_start,path_end,row_start,row_end)
   result = do_request(xmltext)
   data = parse_resultXML(result,type)
   if len(data)>0:
      makeyaml(data,output,type)
   return data

def search(type,date_start,date_end,cloud_start,cloud_end,path_start,path_end,row_start,row_end):
   #path_start = "110"
   #path_end ="110"
   #row_start = "35"
   #row_end = "35"

   xmltext = generate_search_xml(date_start,date_end,cloud_start,cloud_end,path_start,path_end,row_start,row_end)
   result = do_request(xmltext)
   data = parse_resultXML(result,type)
   return data

if __name__ == "__main__":
   #search_and_generate("fine","2014-01-01","2014-12-31","0","100","landsat8.yaml")
   xmltext = generate_search_xml("2014-01-01","2014-12-31","0","100","104","116","28","43")
   result = do_request(xmltext)
   #print result
   data = parse_resultXML(result,"cloud")
   print data