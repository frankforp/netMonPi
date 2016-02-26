# netMonPi
A set of two scripts that allows you to run a simple network connections monitor on your Raspberry Pi. It works by listening to ARP broadcast packets and pings discovered devices from time to time to get their current status. All events are logged.
You can enable notifications to be sent to you using ifttt.com service.

There are some things you'll need or want to change before you start.

Make sure you have a log file - "touch netMonPi.log" 

In netMonPi.py:
 * network = '192.168.1.0/24' #network subnet mask
 * gateway = '192.168.1.1' #ip address of router
 * triggerIFTTT = False

In iftttTrigger.py:
 * KEY = 'YOUR_API_KEY'

Optionally, create a launcher sh script and add it to cron


As part of my uni work this is linked to WikiHow article: http://www.wikihow.com/Monitor-Network-Connections-Using-Raspberry-Pi


Couple of things on to-do list for this:
* add functionality to save log into proper CSV file
* introduce data visualisation
  * could use Google Visualisation API - https://developers.google.com/chart/interactive/docs/reference
  * Lighttpd - http://redmine.lighttpd.net/projects/lighttpd/wiki/TutorialConfiguration
* monitor for deauth packets (very unlikely you can get adversary, but at least you know you're being attacked) - wlan.fc.type_subtype == 0x0C - https://supportforums.cisco.com/document/52391/80211-frames-starter-guide-learn-wireless-sniffer-traces
* introduce network performance monitor - regular upload/download speed checking - http://www.raspberrypi-spy.co.uk/2015/03/measuring-internet-speed-in-python-using-speedtest-cli/
