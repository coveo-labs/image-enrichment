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

def executePixyleAI(file, settings):
  url = 'https://pva.pixyle.ai/v4/solutions/auto-tag/image' 
  headers = { 
      'Authorization': "Bearer "+settings['PixyleApiKey']
  } 
  print (file)

  #curl -H "Content-Type:multipart/form-data" -H "Authorization:Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2NTE3NTk2NDAsIm5iZiI6MTY1MTc1OTY0MCwianRpIjoiYTg5NGE1MDUtMzRmYS00YjJhLWE1NzgtN2E2YTRlNGNjNDYxIiwiaWRlbnRpdHkiOiI5OWI1NWYwMy03NWI1LTRiODMtYTU1MC1hN2UyNjAyNTljNmQiLCJmcmVzaCI6ZmFsc2UsInR5cGUiOiJhY2Nlc3MifQ.6Kw_d-xeMqivcD2x2FUEpjLqvJe5i5UBRncJXNLTZ-k" -F "image=https://fashion.coveodemo.com/images/cn10025257.jpg"  -X POST https://pva.pixyle.ai/v4/solutions/auto-tag/image
  
  response = requests.post(url, headers=headers,data=dict(image=file))#data=data)
  if response.status_code==200: 
    #print(json.dumps(response.json(), indent=2)) 
    return response.json()
  else: 
    print('Error posting API: ' + response.text)
    return None


def loadConfiguration():
  settings={}
  try:
      with open("settings.json", "r",encoding='utf-8') as fh:
        text = fh.read()
        settings = json.loads(text)
  except:
    print ("Failure, could not load settings.json or config.json")
  return settings

def doWeHaveJson(photo):
  newrecord={}
  photo = photo.replace('.jpg','.json')
  photo = photo.replace('images','json')
  path = Path(photo)

  return path.is_file()

def loadJson(photo):
  newrecord={}
  photo = photo.replace('.jpg','.json')
  photo = photo.replace('images','json')
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

def processImage(photo, settings):
  jsondata = loadJson(photo)
  if jsondata:
    image = jsondata['image']
    image = image.replace('\\','//')
    image = image.replace('//','/')
    image = image.replace('https:/','https://')

    data = executePixyleAI(image, settings)
    jsondata['pixyle'] = data
    return jsondata
  return None

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
  title = getKey('Style',jsondata).split(';')[0]+' '+getKey('Color',jsondata)+' '+getKey('Material',jsondata)+' '+getKey('Subcategory',jsondata).split(';')[0]
  title = title.replace('  ',' ')
  jsondata['ProductTitle']=title.title()
  return jsondata

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
      #print (objects)
      cat = ''
      if 'Category' in objects: 
        cat = objects['Category']
      else:
        cat = objects['Top Category']
      if (cat in all_products):
        #if already in products, skip it
        pass
      else:
        clean = createProductName(clean)
        clean['Category'] = cat
        clean['price'] = 10+random.randint(1,20)
        clean['brand'] = retailers[random.randint(0,len(retailers)-1)]
        all_products[cat]=clean

  return all_products

def process():
  #Get All files
  total=0
  settings = loadConfiguration()
  images = glob.glob('..\\images\\*.*',recursive=True)
  for image in images:
    total = total+1
    print ("Processing image: "+image)
    #Check if we have JSON
    if (doWeHaveJson(image)):
      print("Processing: "+image)
      data = processImage(image, settings)
      if data is not None:
        updateJson(image, data)
      # data = loadJson(image)
      # original={}
      # original['raw']=data['records']
      # original['clean']=cleanData(data)
      # if data is not None:
      #   updateJson(image, original)
      # else:
      #   print("ERROR on Processing...")

    else:
      print("N/AProcessing...")

    #break

  #json_dump(DESC_MAP, Path('../outputs/descriptions.json'), sort_keys=True)
  print("We are done!\n")
  print("TAGS/Fields:")
  print (ALLKEYS)
  print("Processed: "+str(total)+" results\n")
  
try:
  #fileconfig = sys.argv[1]
  #process(fileconfig)
  process()
except Exception as e: 
  print(e)
  traceback.print_exception(*sys.exc_info())
  #print ("Specify configuration json (like config.json) on startup")
