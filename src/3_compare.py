import sys
import os
import json
import traceback
import re
import base64
import operator
import math
import csv
import random
from pathlib import Path
import requests 
import glob

ALLKEYS=[]

def json_dump(data, file_name, indent=2, sort_keys=False):
  with open(file_name, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=indent, sort_keys=sort_keys, check_circular=False)


def json_load(file_name):
  data = {}
  with open(file_name, 'r', encoding='utf-8') as f:
    data = json.load(f)

  return data


def loadJson(photo):
  newrecord={}
  with open(photo, "r",encoding='utf-8') as fh:
        text = fh.read()
        newrecord = json.loads(text)
  return newrecord

def updateJson(photo, updaterec):
  photo = photo.replace('.jpg','.json')
  photo = photo.replace('images','json')
  try:
       with open(photo, "w", encoding='utf-8') as handler:
         text = json.dumps(updaterec, ensure_ascii=True)
         handler.write(text)
  except:
    pass
  return updaterec

def addMeta(key, value, data):
  if key in data:
    data[key] = data[key]+';'+value
  else:
    data[key] = value
  return data

def addTagMeta(key, jsondata, data):
  if key in jsondata['_tags']:
    value = ''
    for sub in jsondata['_tags'][key]:
      if value=='':
        value = sub['name']
      else:
        value += ';'+sub['name']
    if key in data:
      data[key] = data[key]+';'+value
    else:
      data[key] = value
  return data

def addAllTags(jsondata, data):
  global ALLKEYS
  for key in jsondata['_tags'].keys():
    if key in ALLKEYS:
      pass
    else:
      ALLKEYS.append(key)
    data = addTagMeta(key,jsondata,data)
  return data

def getKey(key, jsondata):
  if key in jsondata:
    return jsondata[key]
  else:
    return ''

def createProductName(jsondata):
  #Color, Material, First SubCategory
  title = getKey('Style',jsondata).split(';')[0]+' '+getKey('Color',jsondata).split(';')[0]+' '+getKey('Material',jsondata).split(';')[0]+' '+getKey('Subcategory',jsondata).split(';')[0]
  title = title.replace('  ',' ').title()
  #jsondata['ProductTitle']=title.title()
  return title

def cleanData(jsondata):
  all_products={}
  retailers = ["Adidas",
        "American Eagle","Armani","Banana Republic","Benetton","Brixton","CMP","Ralph Lauren","Timberland"]
  for record in jsondata['records']:
    for objects in record['_objects']:
      #Each object is a product...
      
      clean = {}
      #is already in _tags
      #clean = addMeta('Category',objects['Category'],clean)
      clean = addMeta('Tags',objects['_tags_simple'],clean)
      clean = addAllTags(objects,clean)
      if (objects['Category'] in all_products):
        #if already in products, skip it
        pass
      else:
        clean = createProductName(clean)
        clean['price'] = 10+random.randint(1,20)
        clean['brand'] = retailers[random.randint(0,len(retailers)-1)]
        all_products[objects['Category']]=clean

  return all_products


def createCategoriesPaths(categories):
  catpath=''
  catpaths=[]
  for cat in categories:
     if catpath=='':
       catpath=cat #man
       catpaths.append(catpath)
     else:
       catpath=catpath+'|'+cat
       catpaths.append(catpath)
  #catpaths = list(set(catpaths))
  return catpaths

def createCategoriesSlug(categories):
  slug=[]
  catpath=''
  for cat in categories:
    cat=cat.lower().replace(' ','-')
    if catpath=='':
      catpath=cat #man
      slug.append(catpath)
    else:
      catpath=catpath+'/'+cat
      slug.append(catpath)
  
  #slug = list(set(catpaths))

  return slug

def createCategories(jsondata):
  categories=[]
  genders=' and '.join(getKey('Gender',jsondata).split(';'))
  categories.append(genders)
  for cat in getKey('Category',jsondata).split('/'):
      categories.append(cat)

  return categories


def createCategoriesNoGender(jsondata):
  categories=[]
  #genders=' and '.join(getKey('Gender',jsondata).split(';'))
  #categories.append(genders)
  for cat in getKey('Category',jsondata).split('/'):
      categories.append(cat)

  return categories


def addMeta(key, value, data):
  if key in data:
    data[key] = data[key]+';'+value
  else:
    data[key] = value
  return data

def addTagMeta(key, jsondata):
  if key in jsondata['_tags']:
    value = ''
    for sub in jsondata['_tags'][key]:
      if value=='':
        value = sub['name']
      else:
        value += ';'+sub['name']
  return '<tr><td>'+key+'</td><td>'+value+'</td></tr>'

def addAllTags(jsondata):
  data=''
  for key in jsondata['_tags'].keys():
    data += addTagMeta(key,jsondata)
  return data

def save(html,nr):
    file_object = open('compare'+str(nr)+'.html', 'w', encoding="utf-8")
    file_object.write(html)
    file_object.close()

def process():
  #Get All files
  total=0
  all_json=[]
  all_keys=[]
  sku_counter=1
  html = "<html><body><html><table border=1>"
  images = glob.glob('..\\json\\*.json',recursive=True)
  nr = 1
  for image in images:
    print ("Processing image: "+image)
    #Check if we have JSON
    if(len(html)>50000):
      html+="</table></body></html>"
      save(html,nr)
      nr=nr+1
      html = "<html><body><html><table border=1>"

    data = loadJson(image)
    if 'pixyle' in data:
      data['image'] = data['image'].replace('\\','//')
      data['image'] = data['image'].replace('//','/')
      data['image'] = data['image'].replace('https:/','https://')

      html+="<tr><td>"+image+"</td><td><img width=200px src='"+data['image']+"'/></td></tr>"
      html+="<tr><td>"+"Ximilar AI</td><td>Pixyle</td></tr>"
      
      pixyle = data['pixyle']
      if pixyle:
        no_object_pixyle = pixyle['meta']['counter_products']
        no_object_ximilar=0
        no_of_attributes_pixyle = 0
        pixyle_values=""
        ximilar_values=""
        for res in pixyle['result']:
          for rec in res['detected_attributes_types']:
            for val in rec['attributes']['correct']:
              pixyle_values +="<tr><td>"+rec["attribute_type"]+'</td><td>'+val['attribute']+'</td></tr>'
              no_of_attributes_pixyle += 1
        
        for record in data['raw']['records']:
          for objects in record['_objects']:
            no_object_ximilar+=1
            ximilar_values += addAllTags(objects)
            ximilar_values += "<tr><td colspan=2><hr></td></tr>"
        
        html+="<tr><td >"+str(no_object_ximilar)+"</td><td>"+str(no_object_pixyle)+"</td></tr>"
        html+="<tr><td valign=top><table>"+ximilar_values+"</table></td><td valign=top><table>"+pixyle_values+"</table></td></tr>"
 
  html+="</table></body></html>"
  save(html,nr)

      #break

  html+="</table></body></html>"

  print("We are done!\n")
  print("All keys:")
  print(all_keys)
  print("Processed: "+str(total)+" results\n")
  
try:
  #fileconfig = sys.argv[1]
  #process(fileconfig)
  process()
except Exception as e: 
  print(e)
  traceback.print_exception(*sys.exc_info())
  #print ("Specify configuration json (like config.json) on startup")
