import asyncio
import sys, os
import time as tt

servers = { "Alford" : {
    "friends" : ["Hamilton", "Welsh"],
    "port" : 8610,},
            "Ball" : {
                "friends" : ["Holiday", "Welsh"],
                "port" : 8611,},
            "Hamilton" : {
                "friends" : ["Holiday"],
                "port" : 8612,},
            "Holiday": {
                "friends" : ["Ball", "Hamilton"],
                "port" : 8613,},
            "Welsh" : {
                "friends" : ["Alford", "Ball"],
                "port" : 8614,}
}

if(len(sys.argv) != 2):
    raise ValueError("Expected 1 argument (serverName)")
else:
    if sys.argv[1] not in servers:
        raise ValueError("Please enter a valid server name")
    else:
        serverName = sys.argv[1]



class EchoClientProtocol(asyncio.Protocol):
    def __init__(self, message, loop):
        self.message = message
        self.loop = loop

    def connection_made(self, transport):
        transport.write(self.message.encode())
        print('Data sent: {!r}'.format(self.message))

    def data_received(self, data):
        print('Data received: {!r}'.format(data.decode()))

    def connection_lost(self, exc):
        print('The server closed the connection')
        print('Stop the event loop')
        self.loop.stop()

loop = asyncio.get_event_loop()
time = tt.time()
message = 'IAMAT kiwi.cs.ucla.edu +34.068930-118.445127 ' + str(time) + '\n'
portNum = servers[serverName]["port"]
coro = loop.create_connection(lambda: EchoClientProtocol(message, loop),
                              '127.0.0.1', portNum)
loop.run_until_complete(coro)
loop.run_forever()
loop.close()