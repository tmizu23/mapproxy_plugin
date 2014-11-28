import os, sys, httplib
from xml.etree import ElementTree
from datetime import date

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

def parse_resultXML(result,type):
   root = ElementTree.fromstring(result)
   namespace ={'rim':'urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0'}
   namespace2 ={'gml':'http://www.opengis.net/gml'}
   

   es = root.findall(".//rim:Value",namespace)
   i=iter(es)
   data=[]
   pathrow={}

   for e1,e2,e3,e4,e5,e6,e7,e8,e9,e10,e11,e12,e13,e14,e15,e16,e17,e18,e19,e20,e21,e22 in zip(i,i,i,i,i,i,i,i,i,i,i,i,i,i,i,i,i,i,i,i,i,i):
     
      date = e7.text
      cloud = e14.text
      id = e22.text.split("/")[4].split("?")[0]
      pr = e8.text+","+e9.text
      if pathrow.has_key(pr):
         use='no'
         if (type=="fine" and pathrow[pr]['mincloud'] > float(cloud)) or ( type=="cloudy" and pathrow[pr]['mincloud'] < float(cloud) ):
              data[pathrow[pr]['num']]['use']='no'
              pathrow[pr]={'num':len(data),'mincloud':float(cloud)}
              use='yes'
      else:
         use='yes'
         pathrow[pr]={'num':len(data),'mincloud':float(cloud)}

      data.append({'id':id,'pr':pr,'date':date,'cloud':cloud,'use':use})
 
   es = root.findall(".//gml:LinearRing",namespace2)
   k=0
   for e in es:
       hh = e.findall(".//gml:pos",namespace2)
       h=iter(hh)

       for h1,h2,h3,h4,h5 in zip(h,h,h,h,h):
          p1 = h1.text.split(' ')
          p2 = h2.text.split(' ')
          p3 = h3.text.split(' ')
          p4 = h4.text.split(' ')
          w = str(round(min(float(p1[0]),float(p4[0])),2))
          e = str(round(max(float(p2[0]),float(p3[0])),2))
          n = str(round(min(float(p1[1]),float(p2[1])),2))
          s = str(round(max(float(p3[1]),float(p4[1])),2))
          
       data[k]['bbox']=",".join([w,s,e,n])
       #print data[k]
       k=k+1
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
   #attribution:
   #   text: "Image produced and distributed by AIST, Source of Landsat 8 data: U.S. Geological Survey."
   md:
      title: Landsat8
      abstract: "Image produced and distributed by AIST, Source of Landsat 8 data: U.S. Geological Survey."
      online_resource: http://landsat8.geogrid.org/l8/index.php/ja/
      access_constraints:
            Read the Terms of Use.<br />
            <a href="http://landsat8.geogrid.org/l8/index.php/ja/service-3">http://landsat8.geogrid.org/l8/index.php/ja/service-3</a>
            
layers:
  - name: TITLE_TEMPLATE
    title: TITLE_TEMPLATE
    sources: [TITLE_TEMPLATE]
    min_res: 4800
caches:
  TITLE_TEMPLATE:
    grids: [GLOBAL_GEODETIC,GLOBAL_WEBMERCATOR]
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
   f.close()

def search_and_generate(type,date_start,date_end,cloud_start,cloud_end,output):
   path_start = "104"
   path_end ="116"
   row_start = "28"
   row_end = "43"

   xmltext = generate_search_xml(date_start,date_end,cloud_start,cloud_end,path_start,path_end,row_start,row_end)
   result = do_request(xmltext)
   data = parse_resultXML(result,type)
   makeyaml(data,output,type)

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
   xmltext = generate_search_xml("2014-01-01","2014-12-31","0","100","110","110","35","35")
   result = do_request(xmltext)
   data = parse_resultXML(result,"fine")
   print data