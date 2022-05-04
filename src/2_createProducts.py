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
      if (objects['Category'] in all_products):
        #if already in products, skip it
        pass
      else:
        clean = createProductName(clean)
        clean['price'] = 10+random.randint(1,20)
        clean['brand'] = retailers[random.randint(0,len(retailers)-1)]
        all_products[objects['Category']]=clean

  return all_products

def process():
  #Get All files
  total=0
  all_json=[]
  sku_counter=1
  images = glob.glob('..\\json\\*.json',recursive=True)
  for image in images:
    print ("Processing image: "+image)
    #Check if we have JSON
    data = loadJson(image)
    for key in data['clean']:
      total = total+1
      print ("JSON: "+image+" ==> "+key)
      dataset = data['clean'][key]
      dataset['image'] = data['image']
      dataset['sku'] = 'prt_'+f'{sku_counter:07}'
      dataset['permanentid'] = dataset['sku']

      sku_counter+=1
      all_json.append(dataset)
      #break

  json_dump(all_json, Path('../outputs/products.json'), sort_keys=True)
  print("We are done!\n")
  print("Processed: "+str(total)+" results\n")
  
try:
  #fileconfig = sys.argv[1]
  #process(fileconfig)
  process()
except Exception as e: 
  print(e)
  traceback.print_exception(*sys.exc_info())
  #print ("Specify configuration json (like config.json) on startup")
