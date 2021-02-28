from flask import Flask, session, redirect, url_for, escape, request, flash, render_template
from flask_session import Session
from bs4 import BeautifulSoup
import planisphere
from planisphere import Game, Map, Room
import hashlib
import pickle
import config
import os
from copy import deepcopy
from os import urandom, path


app = Flask(__name__)
app.config.from_object('config.Config')
#app.config.from_envvar('YOURAPPLICATION_SETTINGS')
Session(app)

def pickle_it(data, file_name):
	with open(file_name, 'wb') as f:
		pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)


def unpickle_it(file_name):
	with open(file_name, 'rb') as f:
		return pickle.load(f)


def delete_user_data():
	os.remove('user_adat.pickle')
	os.remove('user_prog.pickle')


if not os.path.isfile('user_adat.pickle'):
	pickle_it({}, 'user_adat.pickle')


if not os.path.isfile('user_prog.pickle'):
	pickle_it({}, 'user_prog.pickle')


def set_soup(markup):
	with open(markup, 'r') as f:
		soup = BeautifulSoup(f, 'lxml')

	return soup


@app.route("/", methods=['GET'])
def index():
	user = session.get('user')
	
	return render_template("landing.html", user=user)

@app.route("/new_game", methods=['GET', 'POST'])
def new_game():
	user = session.get('user')
	soup = set_soup('games.xml')
	games = soup('game')

	if request.method == 'GET':
		session.pop('rooms', None)
		return render_template("new_game.html", games=games, user=user)

	else:
		game_name = request.form['games']
		game_node = soup.find("game", id=game_name)

		active_game, game_map = planisphere.build_game(markup=game_node)
		
		session['active_game'] = repr(active_game)
		session['map'] = repr(game_map)
		
		
		return redirect(url_for("game"))


@app.route("/saved_games", methods=['GET', 'POST'])
def saved_games():
	user = session.get('user')
	user_prog = unpickle_it('user_prog.pickle')
	nothing_saved_yet = {'Empty': {'game': {Game(name='Nothing saved yet!', randoms='', active='')}, 'map': '', 'room': 'Nothing saved yet'}}
	user_games = user_prog.get(user, nothing_saved_yet)


	if request.method == 'GET':
		return render_template("saved_games.html", user=user, games=user_games)

	else:
		game_name = request.form['saved_games']
		load_game_data = user_games.get(game_name)

		session['active_game'] = load_game_data.get('game')
		session['map'] = load_game_data.get('map')

		return redirect(url_for("game"))

@app.route("/game", methods=['GET', 'POST'])
def game():
	user = session.get('user')
	active_game = eval(session.get('active_game'))
	print ('active game type', type(active_game))
	game_map = eval(session.get('map'))
	room = active_game.active_room

	if request.method == 'GET':

		if room:
			return render_template("show_room.html", room=room, user=user)

		else:
			return render_template("you_died.html")

	else:
		action = request.form.get('action')
		
		if room.name and action:
			next_room = room.go(action)

			if not next_room:
				room.attempts -= 1					

				if room.attempts == 0:
					return render_template("you_died.html", room=room, user=user)

			else:
				room = eval(game_map.get(next_room))
			

			active_game.upd_active_room(room)

			if not room.name in ['death', 'The End'] and user:
				user_prog = unpickle_it('user_prog.pickle')
				user_prog[user] = {active_game.name: {'game': repr(active_game), 'map': repr(game_map), 'room': room.name}}
				pickle_it(user_prog, 'user_prog.pickle')
			
			session['active_game'] = repr(active_game)
				
				
		else:
			return render_template("you_died.html")
	
		return render_template("show_room.html", room=room, user=user)

@app.route("/logon", methods=['GET', 'POST'])
def logon():
	error = None
	if request.method == 'POST':
		user_adat = unpickle_it('user_adat.pickle')
		user_prog = unpickle_it('user_prog.pickle')
		user = request.form['username']
		pwd_hash = hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest()
		admin_pwd_hash = 'ab13387f24af50f9835f7b089d7a4f46d74a7f053e1090db98ecdb32dbac871b'

		
		if user in user_adat and pwd_hash == user_adat.get(user) or \
			user == 'admin' and pwd_hash == admin_pwd_hash:	
			session['user'] = user

			flash('Your are signed in as {}!'.format(user))
			return render_template("landing.html", user=user)

		else:
			error = 'Invalid credentials!'
	
	return render_template('logon.html', error=error)

@app.route("/logout")
def logout():
	session.pop('user', None)
	session.pop('active_game', None)

	return render_template("landing.html", user=None)

@app.route("/register", methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		
		pwd1 = hashlib.sha256(request.form['regpass1'].encode('utf-8')).hexdigest()
		pwd2 = hashlib.sha256(request.form['regpass2'].encode('utf-8')).hexdigest()
		pwd_blank = hashlib.sha256(''.encode('utf-8')).hexdigest()

		regusr = request.form['regusername']
		game_name = session.get('game_name', None)
		room_name = session.get('room_name', None)
		user_adat = unpickle_it('user_adat.pickle')
		
		if not regusr in user_adat and regusr and len(regusr)>1 and regusr != 'admin':
			if pwd1 == pwd2 and pwd1 != pwd_blank:
				user_adat[regusr] = pwd1
				pickle_it(user_adat, 'user_adat.pickle')
				
				
				if game_name:
					user_prog = unpickle_it('user_prog.pickle')
					user_prog[regusr] = {game_name:room_name}
					pickle_it(user_prog, 'user_prog.pickle')


				session['user'] = regusr
				flash('Your user was registered!')
				return render_template('landing.html', user=regusr)

			else:
				error = 'Your passwords must match and can\'t be blank!'
		
		else:
			error = 'Choose a different, min 2 char long user name!'
			return render_template('logon.html', error=error)

	else:
		return render_template('logon.html', error=error)

@app.route("/delete_user_data", methods=['GET'])
def del_user_dat():
	areuadmin = session.get('user')

	if areuadmin == 'admin':
		delete_user_data()
		pickle_it({}, 'user_adat.pickle')
		pickle_it({}, 'user_prog.pickle')

		flash('User db\'s were recreated')
		return render_template('dashboard.html', user=areuadmin)

	else:
		flash('You have to be an admin to do this')
		return render_template('landing.html')

@app.route("/dashboard", methods=['GET'])
def dashboard():
	user = session.get('user')
	user_prog = unpickle_it('user_prog.pickle')
	game_data = dict()
	
	for usr, data in user_prog.items():
		for game, details in data.items():
			game = eval(details.get('game'))
			game_data[usr] = [game.name, game.rand_vals, game.active_room.name]


	if request.method == 'GET' and user == 'admin':
		return render_template('dashboard.html', user=user, game_data=game_data)

	else:
		pass			
		
if __name__ == "__main__":
	app.run()
