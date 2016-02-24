#-*-coding:utf8-*-

import urllib, urllib2
import json

BASE_URL = 'https://maker.ifttt.com/trigger/'
KEY = 'YOUR_API_KEY'

def send_notification(event, data):
	json_data = urllib.urlencode(data)
	url = BASE_URL + event + '/with/key/'+KEY
	response = urllib2.urlopen(url=url, data=json_data)