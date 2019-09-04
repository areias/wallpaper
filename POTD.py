#!/usr/bin/python3

import urllib.request
import json
from random import *
import os

url="https://magicseaweed.com/api/mdkey/photo?&limit=100&fields=_id,&order_by=dateAdded&order_direction=DESC&potd=true"

req = urllib.request.Request(url)
try:
    response = urllib.request.urlopen(req, timeout=10)
except urllib.error.URLError as e:
    if hasattr(e, 'reason'):
        print('We failed to reach a server.')
        print('Reason: ', e.reason)
    elif hasattr(e, 'code'):
        print('The server couldn\'t fulfill the request.')
        print('Error code: ', e.code)
else:
    text = response.read()
    jsn=json.loads(text.decode('utf-8'))

    n=randint(1,100)

    url = "https://ec2-im-1.msw.ms/md/image.php?id=" + str(jsn[n]['_id']) + "&type=PHOTOLAB&resize_type=STREAM_FULL&fromS3"

    urllib.request.urlretrieve(url, "/home/areias/Downloads/POTD.jpeg")

    os.system("gsettings set org.gnome.desktop.background picture-uri file:///home/areias/Downloads/POTD.jpeg")
    os.system("gsettings set org.gnome.desktop.background picture-options zoom")
	

