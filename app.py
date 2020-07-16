from flask import Flask, session, redirect, url_for, escape, request, flash
from flask import render_template
from bs4 import BeautifulSoup
import planisphere
import os, os.path
import hashlib
import pickle
from os import urandom


app = Flask(__name__)
app.secret_key = os.urandom(16)

def pickle_it(data, file_name):
	with open(file_name, 'wb') as f:
		pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

def unpickle_it(file_name):
	with open(file_name, 'rb') as f:
		return pickle.load(f)

if not os.path.isfile('user_adat.pickle'):
	pickle_it({}, 'user_adat.pickle')

if not os.path.isfile('user_prog.pickle'):
	pickle_it({}, 'user_prog.pickle')

with open('games.xml', 'r') as f:
	soup = BeautifulSoup(f, 'lxml')

def load_game(game_name):
	markup = soup.find("game", id=game_name)
	global game_on
	game_on = planisphere.Game(markup)

global games
games = soup.find_all("game")

@app.route("/", methods=['GET', 'POST'])
def index():

	if request.method == 'POST':
		user = session.get('user')
		return render_template("landing.html", user=user)
	else:
		return render_template("landing.html")

@app.route("/new_game", methods=['GET', 'POST'])
def new_game():
	user = session.get('user')

	if request.method == 'GET':
		return render_template("new_game.html", games=games, user=user)

	else:
		game_name = request.form['games']
		load_game(game_name)

		session['game_name'] = game_name
		session['room_name'] = game_on.START
		
		return redirect(url_for("game"))


@app.route("/saved_games", methods=['GET', 'POST'])
def saved_games():
	user = session.get('user')
	user_prog = unpickle_it('user_prog.pickle')
	data = user_prog.get(user)

	if request.method == 'GET':
		return render_template("saved_games.html", user=user, data=data)

	else:
		game_name = request.form['saved_games']
		load_game(game_name)
		room_name = data.get(game_name)

		session['game_name'] = game_name
		session['room_name'] = room_name

		return redirect(url_for("game"))
		
	
@app.route("/game", methods=['GET', 'POST'])
def game():
	room_name = session.get('room_name')
	user = session.get('user')
	game_name = session.get('game_name')
	load_game(game_name)
	room = game_on.load_room(room_name)
			
	if request.method == 'GET':

		if room_name:
			return render_template("show_room.html", room=room, user=user)

		else:
			return render_template("you_died.html")

	else:
		room.attempts -= 1
		action = request.form.get('action')
		
		if room_name and action:
			next_room = room.go(action)

			if not next_room and room.attempts == 0:
				return render_template("you_died.html")
			
			elif not next_room:
				session['room_name'] = game_on.name_room(room)

			else:
				session['room_name'] = game_on.name_room(next_room)
				
				if not next_room.name in ['death', 'The End'] and user:
					user_prog = unpickle_it('user_prog.pickle')
					user_prog[user] = {session['game_name']:game_on.name_room(next_room)}
					pickle_it(user_prog, 'user_prog.pickle')
		else:
			return render_template("you_died.html")
		
		return redirect(url_for("game"))

@app.route("/logon", methods=['GET', 'POST'])
def logon():
	error = None
	if request.method == 'POST':
		user_adat = unpickle_it('user_adat.pickle')
		user_prog = unpickle_it('user_prog.pickle')
		
		if not request.form['username'] in user_adat or \
			hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest() != \
				user_adat.get(request.form['username']):
			error = 'Invalid credentials!'
		else:
			session['user'] = request.form['username']
			user = session.get('user')

			flash('Your are signed in as {}!'.format(user))					
			return render_template("landing.html", user=user)

			#return render_template("saved_games.html", data=data, user=user)
			
			
			flash('Success! Your previously saved progress was loaded in! You can carry-on!')

			return redirect(url_for('game'))
	
	return render_template('logon.html', error=error)

@app.route("/logout")
def logout():
	session.pop('user', None)
	return render_template("landing.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		
		pwd1 = hashlib.sha256(request.form['regpass1'].encode('utf-8')).hexdigest()
		pwd2 = hashlib.sha256(request.form['regpass2'].encode('utf-8')).hexdigest()
		
		pwd_blank = hashlib.sha256(''.encode('utf-8')).hexdigest()

		regusr = request.form['regusername']
		user_adat = unpickle_it('user_adat.pickle')
		
		if not regusr in user_adat and regusr and len(regusr)>1:
			if pwd1 == pwd2 and pwd1 != pwd_blank:
				user_adat[regusr] = pwd1
				pickle_it(user_adat, 'user_adat.pickle')
				session['user'] = regusr
				user_prog = unpickle_it('user_prog.pickle')
				user_prog[regusr] = {session['game_name']:session['room_name']}
				pickle_it(user_prog, 'user_prog.pickle')

				flash('Your user is registered!')
				return redirect(url_for('logon'))
			else:
				error = 'Your passwords must match and can\'t be blank!'
		
		else:
			error = 'Choose a different, min 2 char long, user name!'
	else:
		return redirect(url_for('/'))

	return render_template("logon.html", error=error)

		
if __name__ == "__main__":
	app.run(debug="True")
