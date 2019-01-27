import logging, time, socket, sys, pickle

logging.basicConfig(level = logging.DEBUG, format = '%(asctime)s - %(message)s')

class Server():
	def __init__(self):
		
		logging.debug('Server Started')
		print('Server\nenter port number or leave this empty to start on default 888')
		self.port = input('port number: ')
		if self.port == '':
			self.port = 888
		print('starting on ' + str(self.port))

		self.port = 888
		self.host = ''
		self.users_list = []
		self.messages_to_send = []
		

		self.transmision_check()
#main server loop
	def transmision_check(self):
		logging.debug(self.users_list)
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		logging.debug('s.s')
		s.bind((self.host, self.port))
		logging.debug('bind')
		while True:
			user_exists = False
			print('listen')
			s.listen()
			conn, addr = s.accept()
			# ~ logging.debug('connectec by ' + str(conn) + 'addr ' + str(addr))
			# ~ with conn:
			print(self.users_list)
			print(self.messages_to_send)
			data_pickle = conn.recv(1024)
			data = pickle.loads(data_pickle)
			print(data)
			if data['message'] == 'echo':
				for i in self.users_list:
					if data['username'] in i:
						print('user exists')
						user_exists = True
						if data['password'] in i:
							print('password correct, logged')
							for i in self.messages_to_send:
								if data['username'] == i['recipient']:
									ii = pickle.dumps(i)
									conn.sendall(ii)
									self.messages_to_send.remove(i)
									print('data to S')
									print('break')
									break
							else:
								conn.sendall(pickle.dumps('echo replay'))
						else:
							print('password wrong')
							conn.sendall(pickle.dumps('echo replay'))
							self.messages_server(data['username'], 'password wrong')
				if user_exists == False:
					print('no user')
					self.users_list.append([data['username'], data['password']])
					print('user added')
					conn.sendall(pickle.dumps('echo replay'))
					self.messages_server(data['username'], 'user created')
				
			else:
				self.messages_to_send.append(data)
				print('message to send added')
				conn.sendall(pickle.dumps('echo replay'))
#server respone generator
	def messages_server(self, username, message):

		data = server_respond = {'sender': 'server', 'recipient': username, 'message': message}
		self.messages_to_send.append(data)


if __name__ == '__main__':
	server = Server()






























