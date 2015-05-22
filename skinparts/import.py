#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
import json


class Skinpart():
    title =  ''
    filename= ''
    link = ''
    category =  ''
    description =  u''
    version = ''
    imagelink = ''
    creator = ''
    dateadded = ''
    def __init__(self = '',  title = '',  filename = '', link = '', category = '',  description  = '', version = '', imagelink = '', creator = '', dateadded = ''):
        self.title = title
        self.filename = filename
        self.link = link
        self.category = category
        self.description = description
        self.version = version
        self.imagelink = imagelink
        self.creator = creator
        self.dateadded = dateadded
    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4,  encoding="utf-8")    
        
skinparts = {'skinparts': {'skinpart': []}}
parts =  []
path =  os.getcwd()
dateadded =  int(time.time())
for file in os.listdir(path):
    if file.endswith(".xml"):
        title =  str(file).replace('.xml',  '').strip()
        screen =  title.split('_')[1].strip()
        creator =  title.split('[')[1].replace(']', '').strip()
        screentitle =  title.split('[')[0].replace('skin_', '').replace('_', ' ').strip()
        category =  title.replace('skin_',  '').split('_')[0].strip()
        filename =  file
        description =  'N/A'
        if os.path.exists(os.path.join(path,  title + '.txt')):
            description =  open(os.path.join(path,  title + '.txt'), 'r').read().decode("ISO-8859-1").encode("utf-8")
        imagelink =  'https://raw.githubusercontent.com/sbeatz/enigma2arcticskin/master/skinparts/' +  title +  '.jpg'
        link =  'https://raw.githubusercontent.com/sbeatz/enigma2arcticskin/master/skinparts/' +  file
        s = Skinpart(title = screentitle, filename = file, link = link, category = category, description = description, version='1.1', imagelink = imagelink, creator = creator, dateadded = dateadded ).to_JSON()
        
        skinparts['skinparts']['skinpart'].append(json.loads(s))
with open("skinparts.json",  "w") as newfile:
    json.dump(skinparts,  newfile, sort_keys = True, indent = 4, encoding="utf8")

