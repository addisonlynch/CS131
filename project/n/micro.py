import socket
import sys, os
from fib import fib 
from collections import deque
from select import select
tasks = deque()


recv_wait={} # Receive socket waiting area
send_wait={} # Send socket waiting area

def run():
	while any([tasks, recv_wait, send_wait]):
		while not tasks:
			# no tasks to run
			# wait for I/O	
			# search for all available tasks in the waiting rooms
			can_recv, can_send, [] = select(recv_wait, send_wait, [])
			# append the tasks to the current tasks
			for s in can_recv:
				tasks.append(recv_wait.pop(s))
			for s in can_send:
				tasks.append(send_wait.pop(s))

		task = tasks.popleft()
		try:
			why, what = next(task) # run to the yield
			if why == 'recv':
				# Must go wait somewhere (it's going to take a minute!)
				# Need a waiting area
				recv_wait[what] = task
			elif why == 'send':
				send_wait[what] = task
			else:
				raise RuntimeError("ARG!")
		except StopIteration:
			print("task done")

def fib_server(address):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind(address)
	sock.listen(5)
	while True:
		yield 'recv', sock
		client, addr = sock.accept() # blocking
		print("Connection", addr)
		tasks.append(fib_handler(client))

def fib_handler(client):
	while True:
		yield 'recv', client
		req = client.recv(100) # blocking
		if not req:
			break
		n = int(req)
		result = fib(n)
		resp = str(result).encode('ascii') + b'\n'
		yield 'send', client
		client.send(resp) # blocking
	print("Closed")

tasks.append(fib_server(('', 25000)))