#-*-coding:utf8-*-
import socket
import struct
import binascii
from datetime import datetime
from time import mktime, sleep
import shlex
import subprocess
import sys
from copy import deepcopy
import iftttTrigger

#dictionary of all currently active devices
networkDevices = {} #ip address (key) => array('mac', 'ip', 'name', 'firstseen', 'lastseen')

rawSocket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))

#friendly names for network event types
arp_Events = {1:'connected', 2:'disappeared', 3:'changed'}

#network parameters
network = '192.168.1.0/24' #network subnet mask
gateway = '192.168.1.1' #ip address of router
thisDeviceIp = ''
pingInterval = 60 #time in seconds between ping actions
lastPingTime = datetime.now()
isConnected = False


def logChanges(clientDetails, event):
    #log all events into log file and trigger IFTTT action for new connections
	with open('netMonPi.log',"a+") as f:
		f.write('\n @'+datetime.now().strftime("%d-%m-%Y %H:%M:%S")+' : '+clientDetails['name'] + ' (' + clientDetails['ip']+ '/' + clientDetails['mac'] +') ' + event)
		f.write(', first spotted on ' + clientDetails['firstseen'] + ' and last seen on ' + clientDetails['lastseen'])

	if event=='connected' or event=='changed':
		to_pass = {}
		to_pass['value1'] = event
		to_pass['value2'] = clientDetails['name']
		to_pass['value3'] = clientDetails['ip'] + '/' + clientDetails['mac']
		iftttTrigger.send_notification('netMonPi', to_pass)
       
def pingDevices():
	#loop through existing entries - if any cannot be resolved, log as disconnected
	global lastPingTime, pingInterval
	diff = mktime(datetime.now().timetuple()) - mktime(lastPingTime.timetuple())
    
	if diff >= pingInterval:
		networkDevicesCheck = deepcopy(networkDevices)
		for ipCheck in networkDevicesCheck:
			networkDevice = networkDevices[ipCheck]
			cmd=shlex.split("ping -c1 "+ipCheck)

			try:
				output = subprocess.check_output(cmd)
			except subprocess.CalledProcessError,e:
				logChanges(networkDevice, arp_Events[2])
				del networkDevices[ipCheck]
		lastPingTime = datetime.now()
                
def main():   
	#start monitoring
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	global isConnected
    
	#need some delay in case Raspberry Pi just connected to network
	while not isConnected:
		try:
			sleep(15)
			s.connect((gateway, 80))
			thisDeviceIP = s.getsockname()[0]
			isConnected = True
		except Exception, e:
			sleep(15)
		    
	#log start-up event
	with open('netMonPi.log',"a+") as f:
		f.write('\n @'+datetime.now().strftime("%d-%m-%Y %H:%M:%S")+' : starup event detected. IP address of this device: '+thisDeviceIP+', gateway: ' +gateway)
    
	#do nmap - for initial discovery of devices on network
	subprocess.Popen(['nmap', network], stdout=subprocess.PIPE)

	while True:
		packet = rawSocket.recvfrom(2048)

		ethernet_header = packet[0][0:14]
		ethernet_detailed = struct.unpack("!6s6s2s", ethernet_header)

		arp_header = packet[0][14:42]
		arp_detailed = struct.unpack("2s2s1s1s2s6s4s6s4s", arp_header)

		#skip non-ARP packets and track only ARP packets going to/from gateway and this device
		sourceIP = socket.inet_ntoa(arp_detailed[6])
		destIP = socket.inet_ntoa(arp_detailed[8])
		ethertype = ethernet_detailed[2]
            
		if ethertype != '\x08\x06' or (ethertype == '\x08\x06' and (sourceIP!=thisDeviceIP and sourceIP!=gateway) and (destIP!=thisDeviceIP and destIP!=gateway)):                
			continue

		macAddress = binascii.hexlify(arp_detailed[5])
		hostName = socket.getfqdn(sourceIP)
		clientDetails = {}      

		#check IP address (might have been assigned to different device)
		addNew = sourceIP!=thisDeviceIP
		if sourceIP in networkDevices:
			clientDetails = networkDevices[sourceIP]

			if clientDetails['mac']==macAddress and clientDetails['name']==hostName:
				addNew=False
				clientDetails['lastseen'] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
				networkDevices[sourceIP] = clientDetails

		if addNew:
			if sourceIP in networkDevices:
				#log that previously logged device is gone and new one exists
				logChanges(clientDetails, arp_Events[3])
                
			clientDetails['mac'] = macAddress
			clientDetails['ip'] = sourceIP                                                           
			clientDetails['name'] = hostName
			clientDetails['firstseen'] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
			clientDetails['lastseen'] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
			networkDevices[sourceIP] = clientDetails

			#log that new device detected
			logChanges(clientDetails, arp_Events[1])
            
		pingDevices()

if __name__ == '__main__':
	main()
