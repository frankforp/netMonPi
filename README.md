# netMonPi
A set of two scripts that allows you to run a simple network connections monitor on your Raspberry Pi. It works by listening to ARP broadcast packets and pings discovered devices from time to time to get their current status. All events are logged.
Optionally you can enable notifications to be sent to you using ifttt.com service.

There are some pthings you'll need or want to change before you start.

Make sure you have a log file - "touch netMonPi.log" 
Add a log for cron - "touch cronlog"

In netMonPi.py:
 * network = '192.168.1.0/24' #network subnet mask
 * gateway = '192.168.1.1' #ip address of router
 * triggerIFTTT = False

In iftttTrigger.py:
 * KEY = 'YOUR_API_KEY'

Optionally, create a launcher script launcher.sh
#!/bin/sh
# launcher.sh
# when Raspberry Pi starts, start python script for monitoring network connections
cd /home/pi/netMonPi
sudo python netMonPi.py

then "chmod 755 launcher.sh"

Add it to cron - "sudo crontab -e" and add
@reboot sh /home/pi/netMonPi/launcher.sh >/home/pi/netMonPi/cronlog 2>&1
