import tkinter, logging, socket, time, pickle, threading, shelve, os
from tkinter.scrolledtext import ScrolledText

logging.basicConfig(level = logging.DEBUG, format = '%(asctime)s - %(message)s')

class Client(tkinter.Tk):
	def __init__(self):
		super(). __init__()
		logging.debug('Client started')
		self.user = {}
		self.contacts = []
#load settings
		if os.path.isfile('settings.bak'):
			settings_obj = shelve.open('settings')
			print(list(settings_obj.keys()))
			if 'user' in list(settings_obj.keys()):
				self.user['username'] = settings_obj['user']
				self.user['password'] = settings_obj['password']
			else :
				self.user = {'username': 'test', 'password': 'test'}
			if 'port' in list(settings_obj.keys()):
				self.port = int(settings_obj['port'])
			else:
				self.port = 888
			if 'host' in list(settings_obj.keys()):
				self.host = settings_obj['host']
			else:
				self.host = '127.0.0.1'	
			if 'contacts' in list(settings_obj.keys()): 
				self.contacts = settings_obj['contacts']
			else:	
				self.contacts = ['Test']
			settings_obj.close()
			print(type(self.port))
			print(type(self.host))
		else:
			self.user = {'username': 'test', 'password': 'test'}
			self.port = 888
			self.host = '127.0.0.1'
			self.contacts = ['Test']
		self.font = ('Tahmona', '8')
		self.messages_to_send = []
		self.child_chat_windows = []

#top menu
		self.menu_bar = tkinter.Menu(self)
		self.file_menu = tkinter.Menu(self.menu_bar, tearoff = 0, font = self.font)
		self.file_menu.add_command(label = 'Add user', command = lambda: self.add_user_to_list(), font = self.font)
		self.file_menu.add_command(label = 'Settings', font = self.font, command = lambda: self.settings())
		self.menu_bar.add_cascade(label = 'settings', menu = self.file_menu, font = self.font)
		self.config(menu = self.menu_bar)
		
#window elements
		self.title('Contact List ' + self.user['username'])
		self.resizable('false','false')
		
		self.who_am_i = tkinter.Label(self, text = self.user['username'])
		self.who_am_i.grid(column = 1, row = 1)
		self.names_list = tkinter.Listbox(self, height = 30, width = 30, font = self.font)
		self.names_list.grid(column = 1, row = 2)
		self.button_start_chat = tkinter.Button(self, text = 'start chat', command = lambda: self.start_chat(), width = 30, font = self.font)
		self.button_start_chat.grid(column = 1, row = 3)
		self.button_add_user = tkinter.Button(self, text = 'remove selected user', command = lambda : self.remove_user_from_list(), width = 30, font = self.font)
		self.button_add_user.grid(column = 1, row = 4)

		self.update_list()
#threads
		t_loop = threading.Thread(target = self.logging_loop, daemon = True).start()
		t_server_connection = threading.Thread(target = self.server_connection, daemon = True).start()

# server connection transporter
	def server_connection(self):
		logging.debug('server_connection')
		#echo frame sender / pass / message - echo
		echo = {'username': self.user['username'], 'password': self.user['password'], 'message': 'echo'}
		echo_pickle = pickle.dumps(echo)
		while True:
			time.sleep(1)
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((self.host, self.port))
			for i in self.messages_to_send:
				self.messages_to_send.remove(i)
				ii = pickle.dumps(i)
				s.sendall(ii)
				break
			s.sendall(echo_pickle)
			data_pickle = s.recv(1024)
			data = pickle.loads(data_pickle)
			if type(data) == dict:
				in_list = False
				for i in self.child_chat_windows:
					if data['sender'] == i.recipient_name:
						in_list = True
				if in_list == True:
					i.text_chat_window.configure(state = 'normal')		
					i.text_chat_window.insert('end', 'from ' + data['sender'] + ': ' + data['message'] + '\n')
					i.text_chat_window.configure(state = 'disabled')
					i.text_chat_window.see('end')
				else:
					self.start_chat(data['sender'])
					for i in self.child_chat_windows:
						if data['sender'] == i.recipient_name:
							i.text_chat_window.configure(state = 'normal')
							i.text_chat_window.insert('end', 'from ' + data['sender'] + ': ' + data['message'] + '\n')
							i.text_chat_window.configure(state = 'disabled')
							i.text_chat_window.see('end')

#update contact list
	def update_list(self, name = None):
		logging.debug('update_list')
		self.names_list.delete('0', 'end')
		if name:
			if name not in self.contacts:
				self.contacts.append(name)
		for i in self.contacts:
			self.names_list.insert('end', i)
		with shelve.open('settings') as settings_obj:
			settings_obj['contacts'] = self.contacts
			settings_obj.close()

#add user to list - class
	def add_user_to_list(self):
		child_client_add_user_window = Client_add_user_window(self)

#remove user from list
	def remove_user_from_list(self):
		self.contacts.remove(self.names_list.get('active'))
		self.update_list()

#start settings window - class
	def settings(self):
		child_settings_window = Settings_window(self)
	
#start chat window - class
	def start_chat(self, recipient = None):
		if recipient == None:
			name_from_list = self.names_list.get('active')
		else:
			name_from_list = recipient
		child_chat_window = Client_chat_window(self, name_from_list)
		self.child_chat_windows.append(child_chat_window)

#logging loop
	def logging_loop(self):
		time.sleep(1)
		while True:
			time.sleep(0.5)
			print(self.child_chat_windows)
			time.sleep(2)
			print(self.messages_to_send)
			for i in self.child_chat_windows:
				print(i.recipient_name)

class Settings_window(tkinter.Toplevel):
	def __init__(self, parent):
		super(). __init__()
		
		self.parent = parent
		self.title('Settings')
# window settings
		self.label_user = tkinter.Label(self, text = 'user', font = self.parent.font)
		self.label_user.grid(column = 1, row = 1)
		self.entry_user = tkinter.Entry(self, width = 30, font = self.parent.font)
		self.entry_user.insert('end', self.parent.user['username'])
		self.entry_user.grid(column = 1, row = 2)
		self.label_password = tkinter.Label(self,text = 'password', font = self.parent.font)
		self.label_password.grid(column = 1, row = 3)
		self.entry_password = tkinter.Entry(self, width = 30, font = self.parent.font)
		self.entry_password.insert('end', self.parent.user['password'])
		self.entry_password.grid(column = 1, row = 4)
		self.label_server = tkinter.Label(self, text = 'server IP', font = self.parent.font)
		self.label_server.grid(column = 1, row = 5)
		self.entry_server = tkinter.Entry(self, width = 30, font = self.parent.font)
		self.entry_server.insert('end', self.parent.host)
		self.entry_server.grid(column = 1, row = 6)
		self.label_port = tkinter.Label(self, text = 'server port', font = self.parent.font)
		self.label_port.grid(column = 1, row = 7)
		self.entry_port = tkinter.Entry(self, width = 30, font = self.parent.font)
		self.entry_port.insert('end', self.parent.port)
		self.entry_port.grid(column = 1, row = 8)
		self.button_ok_save = tkinter.Button(self, text = 'OK & Save', command = lambda: self.ok_save(), font = self.parent.font)
		self.button_ok_save.grid(column = 1, row = 10)
		self.button_ok_save.focus_set()
		self.info_label = tkinter.Label(self, text = 'Restart needed to apply changes', font = ('Impact', '9'))
		self.info_label.grid(column = 1, row = 9)

#save data to file
	def ok_save(self):
		
		data_obj = shelve.open('settings')
		
		data_obj['user'] = self.entry_user.get()
		data_obj['password'] = self.entry_password.get()
		data_obj['host'] = self.entry_server.get()
		data_obj['port'] = int(self.entry_port.get())

		data_obj.close()
		
		self.destroy()


class Client_chat_window(tkinter.Toplevel):
	def __init__(self, parent, recipient_name):
		super(). __init__()
		
		self.parent = parent
		self.recipient_name  = recipient_name
		self.title('Chat with ' + recipient_name)
		self.protocol("WM_DELETE_WINDOW", self.close)
		#normal window
		# ~ self.text_chat_window = tkinter.Text(self, width = 70, height = 15)
		#scrolled window
		self.text_chat_window = ScrolledText(self, width = 70, height = 15)
		self.text_chat_window.grid(column = 1, row = 1)
		self.entry_message_field = (tkinter.Entry(self, width = 65))
		self.entry_message_field.bind('<Return>', self.enter_action)
		self.entry_message_field.grid(column = 1, row = 2)
		self.entry_message_field.focus_set()
		self.text_chat_window.configure(state = 'disabled')
		
	def enter_action(self, event):
		#enter field to chat window
		message = self.entry_message_field.get()
		self.text_chat_window.configure(state = 'normal')
		self.text_chat_window.insert('end', self.parent.user['username'] + ': ' + message + '\n')
		self.text_chat_window.configure(state = 'disabled')
		self.text_chat_window.see('end')
		self.entry_message_field.delete('0', 'end')
		#message to send, whole frame
		message = {'sender': self.parent.user['username'], 'recipient': self.recipient_name, 'message': message}
		self.parent.messages_to_send.append(message)
		
	def close(self):
		for i in self.parent.child_chat_windows:
			if i.recipient_name == self.recipient_name:
				self.parent.child_chat_windows.remove(i)
		self.destroy()

class Client_add_user_window(tkinter.Toplevel):
	def __init__(self, parent):
		super(). __init__()
		
		self.parent = parent
		self.title('Add user...')
		self.entry_add_user = tkinter.Entry(self, width = 30)
		self.entry_add_user.focus_set()
		self.entry_add_user.grid(column = 1, row = 1)
		self.button_ok = tkinter.Button(self, text = 'ok', width = 30, command = lambda: self.button_ok_action())
		self.button_ok.grid(column = 1, row = 2)
		
	def button_ok_action(self):
		name = self.entry_add_user.get().strip()
		self.parent.update_list(name)
		self.destroy()
		
if __name__ == '__main__':
	client = Client()
	client.mainloop()
