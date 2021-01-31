from nose.tools import *
import planisphere
from app import *

app.config['TESTING'] = True
web= app.test_client()

def test_room():
	gold = Room("Goldroom", """This room has gold in it you can grab. 
							There's a door to the north""")
	assert_equal(gold.name, "Goldroom")
	assert_equal(gold.paths, {})

def test_room_paths():
	centre = Room("Centre", "Test room in the centre.")
	north = Room("North", "Test room in the north.")
	south = Room("South", "Test room in the south.") 

	centre.add_path({'north': north, 'south': south})
	assert_equal(centre.go('north'), north)
	assert_equal(centre.go('south'), south)

def test_map():
	start = Room("Start", "You can go west and down a hole.")
	west = Room("Trees", "There are trees here, you can go east")
	down = Room("Dungeon", "It's dark down here, you can go up")


	start.add_path({'west': west, 'down': down})
	west.add_path({'east': start})
	down.add_path({'up': start})
	assert_equal(start.go('west'), west)
	assert_equal(start.go('west').go('east'), start)
	assert_equal(start.go('down').go('up'), start)

def test_gothon_game_map():
	#game = Engine()
	#game.START = 'central_corridor'
	#game.landscape['central_corridor'] = central_corridor
	#game.landscape['laser_weapon_armory'] = laser_weapon_armory
	#game.landscape['generic_death'] = generic_death
	start_room = game.load_room(game.START)
	assert_equal(start_room.go('shoot!'), game.landscape.get('generic_death'))
	assert_equal(start_room.go('dodge!'), game.landscape.get('generic_death'))
	room = start_room.go('tell a joke')
	assert_equal(room, game.landscape.get('laser_weapon_armory'))

def test_gothon_web():
	rv = web.get("/", follow_redirects=True)
	assert_equal(rv.status_code, 200)
	assert_equal(rv.data, b'Central Corridor!')