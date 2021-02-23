
from bs4 import BeautifulSoup
from pprint import pprint
from random import randint

def attempts_exists(tag):
	return tag.has_attr('attempts')

class Room():

	def __init__(self, name=None, description=None, paths={}, attempts=None, hint=None):
		self.name = name
		self.description = description
		self.paths = {}
		self.attempts = int(attempts)
		self.hint = hint
		self.paths.update(paths)
		


	def __repr__(self):
		return f'Room(name="{self.name}", description="""{self.description}""", attempts="{self.attempts}", hint="{self.hint}", paths={self.paths})'

		
	def go(self, direction):
		return self.paths.get(direction, None)

	def add_path(self, paths):
		self.paths.update(paths)


class Game():

	def __init__(self):
		self.map = Map()
		self.rand_vals = {}

	def build_map(self, markup):
		self.soup = BeautifulSoup(str(markup), 'lxml')
		self.name = self.soup.game['id']
		self.START = self.soup.game['start']
		
		for r in self.soup.find_all("room"):
			
			# since attempts or hints doesn't come with every room 
			# first we have to sort which case it is
			if r.find_all(attempts_exists) or r.hint:
				if r['attempts'] and r.hint:
					attempts = int(r['attempts'])
					hint = r.hint.string
				elif r['attemts']:
					hint = 'not available'
				else:
					attempts = 1000

			# now that we are clear on all properties we can build the room object
			room = Room(name=r.title.string, description=r.description.string, attempts=attempts, hint=hint)

			# now we can add the paths to the rooms defined in the xml
			for action in r.path.find_all("action"):
				if 'randint' in action['input']:
					random_value = eval(action['input'])
					room.add_path({str(random_value): action.string})
					self.rand_vals.update({room.name: random_value})
				else:	
					room.add_path({action['input']: action.string}) # self.rooms.get(action.string)

			# finally, when rooms are complete we add them to the map with their id's
			self.map.add_2_map({r['id']: room})		
			
		return self.map	
		# for key, value in self.rooms.items():
		# 	room = self.soup.find("room", id=key)

		# 	for action in room.path.find_all("action"):
		# 		if 'randint' in action['input']:
		# 			random_value = eval(action['input'])
		# 			value.add_path({str(random_value): action.string})
		# 			self.rand_vals.update({value.name: random_value})
		# 		else:	
		# 			value.add_path({action['input']: action.string}) # self.rooms.get(action.string)
		
		# self.START = self.soup.game['start']
		# self.active_room = self.load_room(self.soup.game['start'])
	
	def load_room(self, name):
		return self.rooms.get(name)

	def name_room(self, room):
		for key, value in self.rooms.items():
			if value == room:
				return key


class Map():

	def __init__(self):
		self.map = {}

	def __repr__(self):
		m = {x: repr(y) for x, y in self.map.items()}
		return f'{m}'

	def add_2_map(self, item):
		self.map.update(item)
