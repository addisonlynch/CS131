import asyncio
import os, sys
import time as tt 
from urllib.parse import urlencode
import json
import re
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



if(len(sys.argv) != 2):
    raise ValueError("Expected 1 argument (serverName)")
else:
    if sys.argv[1] not in servers:
        raise ValueError("Please enter a valid server name")
    else:
        serverName = sys.argv[1]

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO, filename=servers[serverName]["log"])

class EchoServerClientProtocol(asyncio.Protocol):
    clients={}

    def tokenize_request(self, request):
        tokens = request.split()
        if not tokens:
            return self.return_invalid_response()
        self.command= tokens[0]
        if self.command == "IAMAT":
            self.blackList = [self.serverName]
            logging.info("Data received from {}: {}".format(self.peername, self.buffer))
            if (len(tokens) != 4) :
                return self.return_invalid_response()
            self.rServer = self.serverName
            self.clientName = tokens[1]
            self.loc = self.validate_loc(tokens[2])
            self.time, skew = self.validate_time(tokens[3])
            self.skew = '+' + str(skew)
            if (not self.loc) or (not self.time) or (self.skew == '+'):
                return self.return_invalid_response()
            if self.clientName in self.clients:
                if self.time < self.clients[self.clientName]["time"]:
                    logging.info("Timestamp of current request predates current database information. Discarding update and returning most recent location.")
                    return self.process_IAMAT()
            self.clients.update({self.clientName: {"loc" : self.loc, "time" : self.time, "skew" : self.skew, "rServer": self.rServer}})
            return self.process_IAMAT()
        elif self.command == "AT":
            logging.info("InterServer data received from {}".format(self.peername))
            self.rServer = tokens[1]
            self.skew = tokens[2]
            self.clientName = tokens[3]
            self.loc = self.validate_loc(tokens[4])
            self.time, _ = self.validate_time(tokens[5])
            self.blackList = tokens[6:]
            if self.serverName not in self.blackList:
                self.blackList.append(self.serverName)
            if self.clientName in self.clients:
                if self.time < self.clients[self.clientName]["time"]:
                    logging.info("Timestamp of current request predates current database information. Discarding update and returning most recent location.")
                    return self.process_AT()
            self.clients.update({self.clientName: {"loc" : self.loc, "time" : self.time, "skew" : self.skew, "rServer": self.rServer}})    
            return self.process_AT()
        elif self.command == "WHATSAT":
            logging.info("Data received from {}: {}".format(self.peername, self.buffer))
            if len(tokens) != 4:
                return self.return_invalid_response()
            self.clientName = tokens[1]
            try:
                self.radius = int(tokens[2])
                self.bound = int(tokens[3])
            except:
                return self.return_invalid_response()
            if not ((0 < self.radius <= 20) and (0 < self.bound <= 50)):
                logging.error("Invalid WHATSAT radius or bound.")
                return self.return_invalid_response()
            return self.process_WHATSAT()
        else:
            logging.info("Data received from {}: {}".format(self.peername, self.buffer))
            self.return_invalid_response()

    @staticmethod
    def validate_time(time):
        ctime = tt.time()
        rtime = float(time)
        if not rtime or rtime < 0:
            return None, None
        sign = '+'
        if ctime < float(time):
            sign = '-'
        skew = ctime - rtime
        logging.info
        return rtime, round(skew, 6) 


    @staticmethod
    def validate_loc(location):
        r = "^[+-](\d{2}|\d{3})\.(\d{1,6})[+-](\d{2}|\d{3})\.(\d{1,6})$"
        if not re.match(r, location):
            return False
        else:
            return location

    def __init__(self, name, loop):
        super().__init__()
        self.loop = loop
        self.serverName = name
        self.buffer = ''

    def connection_made(self, transport):
        self.peername = transport.get_extra_info('peername')
        logging.info('Connection from {} opened'.format(self.peername))
        self.transport = transport

    def connection_lost(self, exc):
        logging.info('Connection from {} closed'.format(self.peername))

    def data_propagate(self, arr):
        arr.extend(self.blackList)
        data = ' '.join(arr) + '\n'
        for friend in servers[self.serverName]["friends"]:
            if friend in self.blackList:
                continue
            logging.info("Propagating to {}".format(friend))
            try:
                factory = self.loop.create_connection(lambda: InterServerProtocol(data), '127.0.0.1', servers[friend]["port"])
            except ConnectionRefusedError:
                logging.error("Error connecting to server: " + friend)
            self.loop.create_task(factory)

    def data_received(self, data):
        self.buffer = self.buffer + data.decode()
        if('\n' in self.buffer):
            message = self.buffer[:self.buffer.index('\n')]
            self.tokenize_request(message)
            self.buffer = self.buffer[self.buffer.index('\n'):]

    def return_invalid_response(self):
        result = '? {0}'.format(self.buffer)
        logging.error("Returned invalid response {}".format(result))
        self.transport.write(result.encode())
        self.transport.close()

    def process_IAMAT(self):
        client = self.clients[self.clientName]
        arr  = ["AT", client['rServer'], client['skew'], self.clientName, client['loc'], str(round(client['time'], 6))]
        result = ' '.join(arr) + '\n'
        logging.info('Send to {}: {!r}'.format(self.peername, result))
        self.transport.write(result.encode())
        logging.info('Close socket with {}'.format(self.peername))
        self.transport.close()          
        logging.info('Propagate data to other servers')
        self.data_propagate(arr)

    def process_AT(self):
        client = self.clients[self.clientName]
        result = ["AT", client['rServer'], client['skew'], self.clientName, client['loc'], str(round(client['time'], 6))]
        self.transport.close()
        logging.info('Closing peer connection from {}'.format(self.peername))
        logging.info('Propagate data to other servers')
        self.data_propagate(result)

    def process_WHATSAT(self):
        params={}
        try: 
            location = self.clients[self.clientName]["loc"]
            found = location.find('+', 1)
            if found == -1:
                found = location.find('-', 1)
            flocation = ','.join([location[:found], location[found:]])        
        except:
            self.return_invalid_response()
        params.update({"radius" : self.radius,
        "location" : location,
        "key" : API_KEY})
        url = GP_URL_ROOT + "radius={0}&location={1}&key={2}".format(self.radius, flocation, API_KEY)
        request = ('GET {0} HTTP/1.1\r\nHost: {1}\r\nContent-Type: text/plain; charset=utf-8\r\n\r\n'.format(url, GP_HOST))
        factory = self.loop.create_connection(lambda: GoogleProtocol(request, self.loop, self), GP_HOST, 'https', ssl=True)
        self.loop.create_task(factory)

    def whatsat_callback(self, response):
        rawjson = response[response.index('{'):response.rindex('}')+1]
        pjson = json.loads(rawjson)
        del pjson['results'][self.bound:]
        strjson = json.dumps(pjson, indent=3).rstrip()
        tstr = ''
        while(tstr != strjson):
            tstr = strjson
            strjson = strjson.replace('\n\n', '\n')
        strjson = strjson + '\n\n'
        client =self.clients[self.clientName]
        fullresponse = 'AT {} {} {} {} {}\n{}'.format(client['rServer'],
            client["skew"], self.clientName, ''.join(client["loc"]),  client["time"],
            strjson)        
        self.transport.write(fullresponse.encode())
        self.transport.close()

    def eof_received(self):
        logging.info("End of Client data input.")
        self.tokenize_request(self.buffer)

class InterServerProtocol(asyncio.Protocol):

    def __init__(self, data):
        super().__init__()
        self.data = data 

    def connection_made(self,  transport):
        self.peername = transport.get_extra_info('peername')
        logging.info('Peer connection to {} opened'.format(self.peername))
        self.transport = transport
        transport.write(self.data.encode())

    def connection_lost(self, exc):
        logging.info("Connection to peer {0} closed".format(self.peername))

class GoogleProtocol(asyncio.Protocol):
    def __init__(self, message, loop, mainprotocol):
        super().__init__()
        self.message = message
        self.loop = loop
        self.protocol = mainprotocol
        self.buffer = ''
        
    def connection_made(self, transport):
        logging.info("Querying Google Places API...")
        self.transport = transport
        transport.write(self.message.encode())

    def data_received(self, data):
        self.buffer = self.buffer + data.decode()
        if(self.buffer[len(self.buffer) - 4:] == '\r\n\r\n'):
            self.transport.close()
            self.loop.call_soon(self.protocol.whatsat_callback, self.buffer)

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