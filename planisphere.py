
from bs4 import BeautifulSoup
from pprint import pprint

def attempts_exists(tag):
	return tag.has_attr('attempts')

class Room():

	def __init__(self, name, description, attempts=None, hint=None):
		self.name = name
		self.description = description
		self.paths = {}
		self.attempts = int(attempts)
		self.hint = hint

	def go(self, direction):
		return self.paths.get(direction, None)

	def add_path(self, paths):
		self.paths.update(paths)


class Game():

	def __init__(self, markup):
		self.soup = BeautifulSoup(str(markup), 'xml')
		self.START = self.soup.game['start']
		self.rooms = {}
		self.build_rooms()

	def build_rooms(self):
		for room in self.soup.find_all("room"):
			room_name = room['id']
			if room.find_all(attempts_exists) or room.hint:
				if room['attempts'] and room.hint:
					attempts = room['attempts']
					hint = room.hint.string
				elif room['attemts']:
					hint = 'not available'
				else:
					attempts = 1000
					
				
			room_name = Room(room.title.string, room.description.string, attempts=attempts, hint=hint)
			self.rooms[room['id']] = room_name
			
		for key, value in self.rooms.items():
			
			room = self.soup.find("room", id=key)

			for action in room.path.find_all("action"):
				value.add_path({action['input']:self.rooms.get(action.string)})
		
		self.START = self.soup.game['start']
		
	
	def load_room(self,name):
		return self.rooms.get(name)

	def name_room(self, room):
		for key, value in self.rooms.items():
			if value == room:
				return key