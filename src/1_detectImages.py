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

def executeXimilar(file, settings):
  url = 'https://api.ximilar.com/tagging/fashion/v2/detect_tags_all' 
  headers = { 
      'Authorization': "Token "+settings['XimilarApiKey'], 
      'Content-Type': 'application/json' 
  } 
  with open(file, "rb") as image_file: 
      encoded_string = base64.b64encode(image_file.read()).decode('utf-8') 
  
  data = { 
      'records': [ {"_base64": encoded_string } ] 
  } 
  
  response = requests.post(url, headers=headers, data=json.dumps(data)) 
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
  data = executeXimilar(photo, settings)
  return data

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
      print("Already processed, skipping. Ximilar")
      # data = loadJson(image)
      # original={}
      # original['raw']=data['records']
      # original['clean']=cleanData(data)
      # if data is not None:
      #   updateJson(image, original)
      # else:
      #   print("ERROR on Processing...")

    else:
      print("Processing...")
      data = processImage(image, settings)
      original={}
      original['raw']=data
      original['image'] = image.replace('..\\','https://fashion.coveodemo.com//')
      #print (data)
      if data is not None:
        original['clean']=cleanData(data)
        updateJson(image, original)
      else:
        print("ERROR on Processing...")

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
