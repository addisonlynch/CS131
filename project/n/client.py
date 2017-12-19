# Time of a long running request


import socket
import time
import os, sys
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 25000))


n = 0

from threading import Thread 
def monitor():
	print("hello world!")
	global n
	while True:
		time.sleep(1)
		print(n, 'reqs/sec')
		n = 0

t =Thread(target=monitor)
t.start()


while True:
	sock.sendall(b'1')
	resp = sock.recv(100)
	n += 1
