import asyncio
import os, sys
import time as tt 
from urllib.parse import urlencode
import json

import logging


API_KEY = "AIzaSyAZapK4Vt5tNI_w7tu0h02Dqh_qDqwARgY"
GP_URL_ROOT = "/maps/api/place/nearbysearch/json?"
GP_HOST = 'maps.googleapis.com'
servers = { "Alford" : {
	"friends" : ["Hamilton", "Welsh"],
	"port" : 8610,
	"log" : "log_alford.log"},
			"Ball" : {
				"friends" : ["Holiday", "Welsh"],
				"port" : 8611,
				"log" : "log_ball.log"},
			"Hamilton" : {
				"friends" : ["Holiday"],
				"port" : 8612,
				"log" : "log_hamilton.log"},
			"Holiday": {
				"friends" : ["Ball", "Hamilton"],
				"port" : 8613,
				"log" : "log_holiday.log"},
			"Welsh" : {
				"friends" : ["Alford", "Ball"],
				"port" : 8614,
				"log" : "log_welsh.log"}
}

clients={}

if(len(sys.argv) != 2):
	raise ValueError("Expected 1 argument (serverName)")
else:
	if sys.argv[1] not in servers:
		raise ValueError("Please enter a valid server name")
	else:
		serverName = sys.argv[1]

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

class EchoServerClientProtocol(asyncio.Protocol):

	# check if coordinate string is properly formated
	@staticmethod
	def validate_request(request):

		if not location[0] in ['+', '-']:
			raise ValueError;
		tokens = None
		index = -1
		for i in range(1, len(location)):
			if location[i] == '+' or location[i] == '-':
				tokens = (location[:i], location[i:])
				index = i
				break			
		if tokens == None:
			raise ValueError;


	def __init__(self, name, loop):
		self.loop = loop
		self.name = name
		self.buf = ''
		self.clients=clients

	def connection_made(self, transport):
		self.peername = transport.get_extra_info('peername')
		logging.info('Connection from {} opened'.format(self.peername))
		self.transport = transport

	def connection_lost(self, exc):
		logging.info('Connection from {} closed'.format(self.peername))


	def data_propagate(self, data):
		for friend in servers[self.name]["friends"]:
			logging.info("Propagating to {}".format(friend))
			try:
				factory = self.loop.create_connection(lambda: InterServerProtocol(data), '127.0.0.1', servers[friend]["port"])
			except :
				logging.error("Error connecting to server: " + friend)
			self.loop.create_task(factory)


	def data_received(self, data):
		logging.info("Receiving data from {}".format(self.peername))
		self.buf = self.buf + data.decode()
		self.return_response(self.buf)
		self.buf = ''

	def return_invalid_response(self):

		result = '? {0}'.format(self.buf)
		logging.error("Returned invalid response {}".format(result))
		self.transport.write(result.encode())
		self.transport.close()


	def return_response(self, message):
		logging.info('Data received from {}: {!r}'.format(self.peername,message))
		mList = message.split()
		if not mList or len(mList) is 0:
			return
		self.now = tt.time()
		self.command = mList[0]
		self.clientName = mList[1]

		if self.command == "IAMAT":
			
			#TODO, split these
			latlon = mList[2]
			time = mList[3]
			clockSkew = self.now - float(time)
			self.clients.update({self.clientName: {"loc" : latlon, "time" : time, "clockSkew" : clockSkew}})
			result = ' '.join(["AT", self.name, str(clockSkew), self.clientName, latlon, time])
			logging.info('Send to {}: {!r}'.format(self.peername, result))
			self.transport.write(result.encode())
			logging.info('Close socket with {}'.format(self.peername))
			self.transport.close()			
			logging.info('Propagate data to other servers')
			self.data_propagate(result)
		elif self.command == "AT":
			self.transport.close()
			logging.info('Closing peer connection from {}'.format(self.peername))
		elif self.command == "WHATSAT":
			#if len(mList) != 4 or int(mList[2]) > 50 or int(mList[3] > 20):
			#	raise ValueError("Please input the correct WHATSAT parameters")
			params={}
			self.bound = mList[3]
			try: 
				bLoc = self.clients[mList[1]]["loc"]
				found = bLoc.find('+', 1)
				if found == -1:
					found = bLoc.find('-', 1)
				location = str(bLoc[:found] + ',' + bLoc[found:])				
			except:
				self.return_invalid_response()

			params.update({"radius" : mList[2],
			"location" : location.encode('utf-8'),
			"key" : API_KEY})
			# FIX BACK TO URLENCODE
			url = GP_URL_ROOT + "radius={0}&location={1}&key={2}".format(mList[2], location, API_KEY)
			request = ('GET {0} HTTP/1.1\r\nHost: {1}\r\nContent-Type: text/plain; charset=utf-8\r\n\r\n'.format(url, GP_HOST))
			factory = self.loop.create_connection(lambda: GoogleProtocol(request, self.loop, self), GP_HOST, 'https', ssl=True)
			self.loop.create_task(factory)

	def whatsat_callback(self, response):
		rawjson = response[response.index('{'):response.rindex('}')+1]
		json_data = json.loads(rawjson)
		intbound = int(self.bound)
		del json_data['results'][intbound:]
		str_data = json.dumps(json_data, indent=4)
		str_data.replace('\n\n', '\n')
		reponse = "AT {0} {1} {2} {3}\n {4}".format(self.name, self.clients[self.clientName]["clockSkew"], self.clients[self.clientName]["loc"], self.clients[self.clientName]["time"], str_data)
		transport.write(response)
		transport.close()

	def eof_received(self):
		logging.info("End of Client data input.")
		self.return_response(self.buf)


class InterServerProtocol(asyncio.Protocol):

	def __init__(self, data):
		self.data = data 

	def connection_made(self, transport):
		self.peername = transport.get_extra_info('peername')
		logging.info('Peer connection to {} opened'.format(self.peername))
		self.transport = transport
		transport.write(self.data.encode())
		transport.close()

	def connection_lost(self, exc):
		logging.info("Connection to peer {0} lost".format(self.peername))

class GoogleProtocol(asyncio.Protocol):
	def __init__(self, message, loop, mainprotocol):
		self.message = message
		self.loop = loop
		self.prot = mainprotocol
		self.buf = ''
		
	def connection_made(self, transport):
		self.transport = transport
		transport.write(self.message.encode())

	def data_received(self, data):
		self.buf = self.buf + data.decode()
		if(self.buf[len(self.buf) - 4:] == '\r\n\r\n'):
			self.transport.close()
			self.loop.call_soon(self.prot.whatsat_callback, self.buf)

loop = asyncio.get_event_loop()
# Each client connection will create a new protocol instance
coro = loop.create_server(lambda: EchoServerClientProtocol(serverName, loop), '127.0.0.1', servers[serverName]["port"])
server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
logging.info("Started")
try:
	loop.run_forever()
except KeyboardInterrupt:
	logging.info("Shutdown")

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close() 