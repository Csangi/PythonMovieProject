import sqlite3

NEW_OPENMATCH = "INSERT INTO OpenMatches(UserID, MovieID, MovieName) VALUES (?,?,?);"
NEW_USER ="INSERT INTO UserInfo(Name, Password, UserID, Preferences, Contact, Role) VALUES (?,?,?,?,?, ?);"
NEW_MATCH ="INSERT INTO Matches(UserID_One, UserID_Two, MovieID, MovieName) VALUES (?,?,?,?);"
REMOVE_OPENMATCH = "DELETE FROM OpenMatches WHERE MovieID = ?"

def connect():
    return sqlite3.connect("TinMovie.db")


def make_tables(con):
    with con:
        con.execute(
            "CREATE TABLE UserInfo(Name TEXT, Password TEXT, UserID INTEGER PRIMARY KEY, Preferences TEXT, Contact TEXT, Role INTEGER);"
        )
        con.execute(
            "CREATE TABLE Matches(UserID_One INTEGER, UserID_Two INTEGER, MovieID TEXT, MovieName TEXT, FOREIGN KEY(UserID_One) REFERENCES UserInfo(UserID), FOREIGN KEY(UserID_Two) REFERENCES UserInfo(UserID));"
        )
        con.execute(
            "CREATE TABLE OpenMatches(UserID INTEGER, MovieID TEXT PRIMARY KEY, MovieName TEXT, FOREIGN KEY(UserID) REFERENCES UserInfo(UserID));"
        )





def add_user(con, name, password, user_id, preferences, contact, Role):
    with con:
        con.execute(NEW_USER, (name, password, user_id, preferences, contact, Role))

def add_match(con, user_one, user_two, movie_id, movie_name):
    with con:
        con.execute(NEW_MATCH, (user_one, user_two, movie_id, movie_name))

def add_open_match(con, user, movie_id, movie_name):
    with con:
        con.execute(NEW_OPENMATCH, (user, movie_id, movie_name))

def remove_open_match(con, movie_id):
    with con:
        con.execute(REMOVE_OPENMATCH, (movie_id))