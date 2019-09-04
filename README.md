

# Automatically update your wallpaper with Magicseaweed's Photo of The Day 


Python script that downloads a photo from Magicseaweed's photo of the day archives and sets it as background wallpaper. Built using Python 3 and Ubuntu 16.04. 


## Inspect the Photo of the Day page

My favourite surf forecast site also has some epic surf photos.

Navigate to https://magicseaweed.com/photos/photo-of-the-day/ and use your browser's developer tools to figure out how we can download a photo. 

Righ click on a photo and choose "Inspect Element". The pertinent tag will be highlighted in blue in the element inspector console that opens up. 

<img src="Screenshot1.png" width="40%" />

What interests us is this tag:

```
<div class="background-cover masonary-image" style="background-image: url(https://ec2-im-1.msw.ms/md/image.php?id=385758&amp;type=PHOTOLAB&amp;resize_type=STREAM_MEDIUM&amp;fromS3);"></div>
```

We can see that this is one of many other similar tags, one for each of the rest of the pictures which we can see are uniquely identified by their id.

We could parse the html with BeautifulSoup and extract the ids, but notice that when you scroll to the bottom you can see that the page dynamically loads more pictures, this suggests that an easier alternative is to try to intercept the AJAX calls from the page and reproduce/replay them.


## Intercepting AJAX calls

how to catch AJAX calls and reproduce them using the requests library and the Google Chrome browser.

like undocumented API,

Dynamic pages that are loaded by javascript worth checking out the network tool 

can intercept the requests and see where our pictures are coming from

To begin with it will be empty. This is because the Network view only starts recording information while it is open.
Refresh the page and see what’s being loaded

If we reload the page and see new requests

A good one to check for any data sources is XHR.  In this case there is only one file that is shown in the XHR tab.

photo?callback seems promising so click on this

<img src="Screenshot2.png" width="40%" />

see details on the right, go to response its is 	 

request method is GET GET is used to request data from a specified resource.

right clikc on request, see in new tab for more detials, we can see a jquery object

<img src="Screenshot3.png" width="40%" />


you can use json lint https://jsonlint.com/ a reformatter to pretty print it and see that the text inside the Jquery parantheses structure better will look like

```json
[{
	"_id": 385758,
	"_obj": "Photo",
	"images": {
		"small": {
			"width": 140,
			"height": 140,
			"url": "\/md\/image.php?id=385758&type=PHOTOLAB&resize_type=STREAM_SMALL&fromS3",
			"cdnUrl": "https:\/\/ec2-im-1.msw.ms\/md\/image.php?id=385758&type=PHOTOLAB&resize_type=STREAM_SMALL&fromS3"
		},
		"medium": {
			"width": 640,
			"height": 426,
			"url": "\/md\/image.php?id=385758&type=PHOTOLAB&resize_type=STREAM_MEDIUM&fromS3",
```

now we want to replicat that call and get the data, the headers section to see all the info that goes to the server in the call.

the request url, visible in Headers, 

```
https://magicseaweed.com/api/mdkey/photo?callback=jQuery1102003300840931011728_1552915212212&approved=true&removed=false&depth=2&limit=20&fields=_id,_obj,isApproved,images.small.*,images.medium.*,isRemoved,description,dateAdded,fullPageUrl,views,user.name,spot.name,isPOTD,taken,favouriteCount,location.country.iso,browseSession.hash,browseSession.size,browseSession.currentPosition&order_by=dateAdded&order_direction=DESC&potd=true&_=1552915212213
```

after some experimenting in modying the parameters o see what data is really needed, you can open a console and do various post requests to the request URL

actually simplified headers to 
```
https://magicseaweed.com/api/mdkey/photo?&limit=100&fields=_id,&order_by=dateAdded&order_direction=DESC&potd=true
```

and returns a json-object diretly

<img src="Screenshot4.png" width="40%" />


## Python's urllib module

python script urllib has some tips on error handling https://docs.python.org/3/howto/urllib2.html#handling-exceptions

```python
#!/usr/bin/env python
import urllib.request
import json

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
```


request 100 ids at a time, and randomly choose 1

query their s3 storage directly and some googline shows s3 options instad of medium you can do resize_type=STREAM_FULL


```python
from random import *

n=randint(1,100)

url = "https://ec2-im-1.msw.ms/md/image.php?id=" + str(jsn[n]['_id']) + "&type=PHOTOLAB&resize_type=STREAM_FULL&fromS3"

urllib.request.urlretrieve(url, "/home/areias/Downloads/POTD.jpeg")
```


## Set picture as background

We can also set descktop background directly from th python script by 

```python
import os
os.system("gsettings set org.gnome.desktop.background picture-uri file:///home/areias/Downloads/POTD.jpeg")
os.system("gsettings set org.gnome.desktop.background picture-options zoom")
```

Now we can run our script from the command line:
```bash
$ python3 POTD.py
```

## Automate with cron

Finally, we can make this script start on reboot by adding the following line to crontab by calling `crontab -e`
```bash
@reboot /bin/sleep 60 && /usr/bin/python3 /home/areias/Projects/wallpaper/POTD.py > log 2>&1
```

Saving a log allows you to trouble shoot in case something goes wrong.

Running the script 60 seconds after start up makes sure we don't run into [permissions problems or availability of services](https://unix.stackexchange.com/questions/109804/crontabs-reboot-only-works-for-root)


