from flask import Flask, redirect, render_template, request, url_for, session
import databases
from databases import *
import sqlite3 as sql
import requests
import random


app = Flask(__name__)
app.secret_key='shhh'


def get_random_movie():
    # key from TMDB website which we need for all api requests
    key = "a141575823e91856c7c532de60ea8eb6"
    # This link specifically grabs popular movies so we dont fetch anything irrelevant 
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={key}"

    # use .get() to grab top 20 popular movies and convert from json 
    # they are stored in a dictionary object
    response = requests.get(url).json()

    #for i in response["results"]:
    	#print(i["title"])

    # Grab a random movie using random library, "results" is a key for the dict
    movie = random.choice(response["results"])

    # Grab Poster URL
    poster_url = "https://image.tmdb.org/t/p/w500" + movie["poster_path"]

    #movie, poster_url = get_random_movie()
    #print(movie)
    #print(poster_url)
    return f"{movie['title']}", poster_url

def make_db():
    con = databases.connect()
    databases.make_tables(con)


@app.route('/')
def hello_world():  # put application's code here
    session.pop('loggedin', None)
    session.pop('Username', None)
    session.pop('Password', None)
    return render_template('login.html')

@app.route('/NewUser')
def NewUser():  # put application's code here
    return render_template('NewUser.html')


@app.route('/NewMovie', methods =['POST', 'GET'])
def NewMovie():  # put application's code here
    if(request.method == 'POST'):
        name = request.form.get('name')
        Idnum = request.form.get('Idnum')
    elif(request.method == 'GET'):
        name = request.args.get('name')
        Idnum = request.args.get('Idnum')
    movieTitle, posterURL = get_random_movie()
    return render_template('MoviePage.html', movieTitle=movieTitle, posterURL=posterURL, name = name, Idnum = Idnum)

@app.route('/like', methods =['POST'])
def like():
    #Here we request the variables from the html page so that we can correcly process the input
    movieTitle = request.form.get('movieTitle')
    Idnum = request.form.get('Idnum')
    name = request.form.get('name')
    #We generate the movie title with the first 2 characters of the title and the last 2 characters
    movieID = str(movieTitle[0] + movieTitle[1] + movieTitle[len(movieTitle) - 2] + movieTitle[len(movieTitle) - 1])
    #we connect with the database so that we can grab any open matches
    with sql.connect("TinMovie.db") as con:
        cur = con.cursor()
        cur.execute("SELECT UserID FROM OpenMatches WHERE MovieID = ?", (movieID,))
        result = cur.fetchall()
        #if there is none than we create a new open match
        print(result)
        if len(result) == 0:
            add_open_match(con, Idnum, movieID, movieTitle)
        else:
            otherID, = result[0]
            print(str(otherID) + " " + str(Idnum))
            #if there is already an open match we check to see if it is with themselves
            if int(Idnum) != int(otherID):
                #if not we delete the open match and create a new match
                add_match(con, Idnum, otherID, movieID, movieTitle)
                remove_open_match(con, (movieID,))
        #then after all that we redirect to the newmovie page
        return redirect(url_for('NewMovie', name=name, Idnum=Idnum))

@app.route('/Profile')
def Profile():  # put application's code here
    if 'loggedin' in session:
        con = sql.connect("TinMovie.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        print(session['UserID'])
        cur.execute("SELECT * FROM UserInfo WHERE UserID = ?", (session['UserID'],))
        values = cur.fetchone()
        print(values)
        cur.execute("""SELECT 
                    user1.Name as UserOne, user2.Name as UserTwo, 
                    user1.Contact as u1Contact, user2.Contact as u2Contact, 
                    m.MovieName as Movie
                    FROM Matches m 
                    JOIN UserInfo user1 ON m.UserID_One = user1.UserID 
                    JOIN UserInfo user2 ON m.UserID_Two = user2.UserID
                    WHERE UserID_One = (?) OR UserID_Two = (?)"""
                    ,((session['UserID']), (session['UserID'])) )
        match = cur.fetchall()
        print(match)
        return render_template('Profile.html', values = values, match = match, name = session['Name'], Idnum = session['UserID'])
    return redirect(url_for('adduser'))

@app.route('/newlog', methods =['POST', 'GET'])
def newlog():
    if request.method == 'POST' and 'Name' in request.form and 'Password' in request.form:
        name = request.form['Name']
        passw = request.form['Password']
    con = sql.connect("TinMovie.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM UserInfo WHERE Name = ? AND Password = ?", (name, passw))
    UserInfo = cur.fetchone()
    print(UserInfo)
    if UserInfo:
        session['loggedin']=True
        session['Name'] = UserInfo['Name']
        session['Password']= UserInfo['Password']
        session['UserID']=UserInfo['UserID']
        #session['Role']=UserInfo['Role']
    else:
        msg = "Incorrect username/password"
        return render_template('login.html', msg=msg)

    return redirect(url_for('Profile', name=session['Name'], Idnum=session['UserID'], Role=UserInfo['Role']))
    #return render_template('Profile.html', name = session['Name'], Idnum = session['UserID'])

@app.route('/adduser', methods =['POST', 'GET'])
def adduser():
    if request.method == 'POST' and 'Name' in request.form and 'Password' in request.form:
            name = request.form['Name']
            passw = request.form['Password']
            pref = request.form['Preferences']
            cont = request.form['Contact']
            Idnum = random.randint(1,30000)
            a=input(print("Do you want this user to have privilages?"))
            if a == 'y':
                rol = 1
            else: rol = 0
            print(rol)
            with sql.connect("TinMovie.db") as con:
                add_user(con, name, passw, Idnum, pref, cont, rol)
            msg="Congrats, your registration was succesful, please log in: "
            return render_template('login.html', msg = msg )


@app.route('/allUsers')
def allUsers():
    if (session['Role']!=1):
        return render_template('Profile.html')
    con = sql.connect("TinMovie.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT Name, UserID, Contact, Role FROM UserInfo;")
    all = cur.fetchall()
    print(all)
    return render_template('allUsers.html', all=all)






answer=input("Do you want to create the database? (y/n): ")
if answer == 'y':
    make_db()



if __name__ == '__main__':
    app.run()
