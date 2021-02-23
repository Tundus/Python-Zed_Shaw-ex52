from flask import Flask, session, redirect, url_for, escape, request, flash, render_template
from flask_session import Session
from bs4 import BeautifulSoup
import planisphere
from planisphere import Room
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
		active_game = planisphere.Game()
		game_map = active_game.build_map(game_node) # a game_map object is a dict with id's and room objects
		active_room = game_map.map.get(active_game.START)
		
		session['game_name'] = active_game.name
		session['map'] = repr(game_map)
		session['active_room'] = repr(active_room)
		
		return redirect(url_for("game"))


@app.route("/saved_games", methods=['GET', 'POST'])
def saved_games():
	user = session.get('user')
	user_prog = unpickle_it('user_prog.pickle')
	data = user_prog.get(user, {'Empty': 'Nothing saved yet!'})
	with open('games.xml', 'r') as f:
		soup = set_soup(f)

	if request.method == 'GET':
		return render_template("saved_games.html", user=user, data=data)

	else:
		game_name = request.form['saved_games']
		# game_markup = soup.find('game', id=game_name)
		# active_game = planisphere.Game(game_markup)
		room_name = data.get(game_name)

		session['game_name'] = game_name
		session['room_name'] = room_name

		return redirect(url_for("game"))

	return render_template("show_room.html", room=active_room, user=user)

@app.route("/game", methods=['GET', 'POST'])
def game():
	user = session.get('user')
	map = eval(session.get('map'))
	room = eval(session.get('active_room'))

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
					return render_template("you_died.html", reason='for good')

				else:
					session['active_room'] = repr(room)
					return render_template("show_room.html", room=room, user=user)

			else:
				room = eval(map.get(next_room))
				if not room.name in ['death', 'The End'] and user:
					game_name = session.get('game_name')
					user_prog = unpickle_it('user_prog.pickle')
					user_prog[user] = {game_name: next_room}
					pickle_it(user_prog, 'user_prog.pickle')

				session['active_room'] = repr(room)
				


				
		else:
			return render_template("you_died.html", reason='technical')
	
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

			#return render_template("saved_games.html", data=data, user=user)
			#flash('Success! Your previously saved progress was loaded in! You can carry-on!')
			#return redirect(url_for('game'))
	
	return render_template('logon.html', error=error)

@app.route("/logout")
def logout():
	session.pop('user', None)
	session.pop('game_name', None)
	session.pop('room_name', None)
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
	active_game = pickle.loads(session.get('active_game'))
	active_room = session.get('active_room')

	if active_game:
		randoms = active_game.rand_vals

	else:
		randoms = None

	if request.method == 'GET' and user == 'admin':
		return render_template('dashboard.html', user=user, user_prog=user_prog,\
								 game=active_game, randoms=randoms, room=active_room)

	else:
		pass			
		
if __name__ == "__main__":
	app.run()
