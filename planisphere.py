
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

	def __init__(self, name=None, randoms={}, active=None):
		self.name = name
		self.rand_vals = randoms
		self.active_room = active
			
	def __repr__(self):
		return f'Game(name="{self.name}", randoms={self.rand_vals}, active={self.active_room})'

	def upd_active_room(self, room=None):
		self.active_room = room


class Map():

	def __init__(self):
		self.rooms = {}

	def __repr__(self):
		m = {x: repr(y) for x, y in self.rooms.items()}
		return f'{m}'

	def __len__(self):
		return len(self.rooms)

	def add_2_map(self, item):
		self.rooms.update(item)


def build_game(markup=None):
	game = Game()
	game_map = Map()

	soup = BeautifulSoup(str(markup), 'lxml')
	game.name = soup.game['id']
	
	for r in soup.find_all("room"):
		
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
				game.rand_vals.update({room.name: random_value})
			else:	
				room.add_path({action['input']: action.string}) # self.rooms.get(action.string)

		# finally, when rooms are complete we add them to the map with their id's
		game_map.add_2_map({r['id']: room})

	game.active_room = game_map.rooms.get(soup.game['start'])
	return game, game_map