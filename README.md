# Python-Zed_Shaw-ex52

As the label says on the the tin box, this code is a realisation of Zed Shaw's exercise #52 in his book: Learn Python 3 the Hard Way.

"In this exercise,  we won't make a complete game, but instead we make an 'engine' that can run the game from Exercise #47 in the browser. This will involve refractoring Exercise #43, mixing in the structure Exercise #47, adding autmated tests, and finally creating a web engine that can run the games.
This exercise will be huge, and I can predict you could spend anywhere from a week to months on it before moving on."

Well, several months and a few more grey hair later my solution is up and running. It could be tested on heroku: the-gothon-game.herokuapp.com

Server side session handling makes me smug about this project if I can be honest with you. It gave me a lot of grief and eventually a lot of happy moments too. When it started to work. For that I had to introduce magic methods for Game, Room and Map. It was a heureka moment. For these moments it is worth doing this.

Caveats:
If you put it on the web change the password in my dotenv file. This file is only there for demonstration and local testing. My heroku app has a different password. The dotenv file is created to support development on a local machine. I enclosed it here to 'play with cards down on the table'. 

The game itself is defined in the file game.xml. You can create your own games by studying this file and modifying it to your own needs, ideas and story. The 'engine' will work fine as long as you follow the structure.

Server side session requires flask_session. I chose Redis as my session container. It worked just fine so far.

This game has a lot of features. It helps you with hints, you can register your user and your progress will be auto saved. It supports multiple games, for which your progress will be individually saved. These saved game states could then be retrieved and players could continue with their games. It has a dashboard available for the admin user only. From here all saved game states of every user could be observed with every random value generated for every game.  Storage files could be wiped by the admin too. Very basic stuff but very useful. You can play around the colours in main.css file and add config parameters in cofig.py.
Beside the many features we have a long list of missing functionalities too. I haven't dealt with natural language processing or fiddly interactive features or password change etc. I could have but my point was to make it work on heroku, a remote web server. My app does that job all right so I stopped. Maybe I will return to this project one day.

Enjoy!


