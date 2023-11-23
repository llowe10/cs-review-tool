# tutorial: https://codesource.io/creating-python-socket-server-with-multiple-clients/
# chat room project: https://github.com/IamLucif3r/Chat-On

import socket
from _thread import *
import random
import sqlite3

HOST = '127.0.0.1'
PORT = 1891
QUESTION_LIMIT = 10
DATABASE_NAME = 'game.db'

clients = []
usernames = []
sessions = []
topics = []
dbconnection = sqlite3.connect(DATABASE_NAME, check_same_thread = False)

sessions = {} # {game ID: topic}
gameRooms = {} # {game ID: [(username, player connection)]}

scores = {} # {player username: score}
responseQueue = [] # (player username, response)

def join_game(connection, username):
    # list all available game session IDs and topics
    avail_sess = ""
    for id in sessions:
        avail_sess += (str(id) + " -- " + sessions[id] + "\n")
    connection.sendall(str.encode(f'Available games:\n{avail_sess}'))

    # capture game session ID from client
    while True:
        id = int(connection.recv(2048).decode('utf-8'))
        if id not in sessions:
            connection.sendall(str.encode(f'Game {id} does not exist.\n'))
        else:
            connection.sendall(str.encode(f'Joining game {id}...\n'))
            gameRooms[id].append((username, connection))
            break

def get_scoreboard():
    rankings = sorted(scores.items(), key = lambda x: x[1])
    
    scoreboard = "SCOREBOARD".center(30, " ")
    scoreboard += "\nPLAYER".ljust(15, " ")
    scoreboard += "SCORE".rjust(15, " ")
    scoreboard += "\n"

    rank = 1
    for tup in rankings:
        result = "{:<10} {:>15}".format(tup[0], tup[1])
        scoreboard += (str(rank) + ". " + result + "\n")
        rank += 1
    
    return scoreboard

def administrate_game(connection, id):
    try:
        cursor = dbconnection.cursor()

        # initalize all player scores to 0
        playersList = gameRooms[id]
        for tup in playersList:
            scores[tup[0]] = 0

        # get questions and related info
        questions = []
        choices = []
        answers = []
        points = []
        topic = sessions[id]
        query = f""" SELECT
                Question, Choice_A, Choice_B, Choice_C, Choice_D, Answer, Points
                FROM QUESTIONS WHERE Topic = \'{topic}\';
                """
        cursor.execute(query)
        result = cursor.fetchall()
        for tup in result:
            questions.append(tup[0])
            choices.append(tup[1] + "\n" + tup[2] + "\n" + tup[3] + "\n" + tup[4] + "\n")
            answers.append(tup[5])
            points.append(tup[6])
        
        # send out questions to users in game room
        for i in range(1, QUESTION_LIMIT + 1):
            # broadcast question and answer choices to users
            connection.sendall(str.encode(f'Question {i}: ' + questions[i]))
            connection.sendall(str.encode(choices[i]))

            # bonus given to first 3 players to respond correctly
            bonusGiven = 0
            for tup in responseQueue:
                if tup[1] == answers[i]:
                    scores[tup[0]] += points[i]

                    if bonusGiven < 3:
                        if bonusGiven == 0:
                            scores[tup[0]] += 100
                        elif bonusGiven == 1:
                            scores[tup[0]] += 75
                        else:
                            scores[tup[0]] += 50
                        bonusGiven += 1

            # broadcast correct answer to players
            connection.sendall(str.encode(answers[i]))

            # broadcast scoreboard to players
            connection.sendall(str.encode(get_scoreboard()))

        # TODO: account for users leaving the session

        # TODO: determine what to do once game ends

        cursor.close()
    except sqlite3.Error as error:
        print('Error occurred - ', error)

def create_game(connection):
    try:
        cursor = dbconnection.cursor()

        # get available topics
        cursor.execute("SELECT Topic FROM QUESTIONS;")
        result = cursor.fetchall()
        for tup in result:
            topics.append(tup[0])

        # list available game topics to client
        avail_topics = ""
        for top in topics:
            avail_topics += (top + "\n")
        connection.sendall(str.encode(f'Available topics:\n{avail_topics}'))

        # capture game topic from client
        while True:
            topic = connection.recv(2048).decode('utf-8')
            if topic not in topics:
                connection.sendall(str.encode(f'Topic \'{topic}\' does not exist.\n'))
            else:
                break
        
        # randomly generate session ID
        id = None
        while True:
            id = random.randint(1000, 9999)
            if id not in sessions:
                sessions[id] = topic
                connection.sendall(str.encode(f'New game created! Session ID: {id}\n'))
                gameRooms[id] = []
                break
        
        connection.sendall(str.encode(f'Waiting for players to join...'))
        confirmation = connection.recv(2048).decode('utf-8')
        if confirmation == 'Y':
            administrate_game(connection, id)
        
        cursor.close()
    except sqlite3.Error as error:
        print('Error occurred - ', error)

def client_handler(connection):
    # get player username
    while True:
        username = connection.recv(2048).decode('utf-8')
        if username not in usernames:
            connection.sendall(str.encode(f'Welcome to CS Review Tool, {username}!\n'))
            clients.append(connection)
            usernames.append(username)
            break
        else:
            connection.sendall(str.encode(f'User {username} already exists.'))
    
    # determine if player wants to create game or join game
    choice = connection.recv(2048).decode('utf-8')
    if choice == 'C':
        create_game(connection)
    else:
        join_game(connection, username)
    
    connection.close()

def accept_connections(ss):
    client, address = ss.accept()
    print("Connected to: " + address[0] + ":" + str(address[1]))
    start_new_thread(client_handler, (client, ))

def start_server(HOST, PORT):
    ss = socket.socket()
    try:
        ss.bind((HOST, PORT))
    except socket.error as e:
        print(str(e))
    
    print(f'Server is listening on port {PORT}...')
    ss.listen()

    load_questions()
    # get_questions()

    while True:
        accept_connections(ss)

def load_questions():
    try:
        cursor = dbconnection.cursor()

        drop_questions_table = 'DROP TABLE IF EXISTS QUESTIONS'
        cursor.execute(drop_questions_table)

        create_questions_table = """ CREATE TABLE QUESTIONS (
                                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                    Topic VARCHAR(25) NOT NULL,
                                    Question VARCHAR(255) NOT NULL,
                                    Choice_A VARCHAR(255) NOT NULL,
                                    Choice_B VARCHAR(255) NOT NULL,
                                    Choice_C VARCHAR(255) NOT NULL,
                                    Choice_D VARCHAR(255) NOT NULL,
                                    Answer VARCHAR(255) NOT NULL,
                                    Difficulty VARCHAR(25) NOT NULL,
                                    Points DOUBLE NOT NULL
                                ); """
        cursor.execute(create_questions_table)
        print("* Questions database table created.")

        cursor.execute('''INSERT INTO QUESTIONS (Topic, Question, Choice_A, Choice_B, Choice_C, Choice_D, Answer, Difficulty, Points) VALUES ('Test', 'What is the answer to question 1?', 'A', 'B', 'C', 'D', 'Answer 1', 'Easy', '25.00')''')
        cursor.execute('''INSERT INTO QUESTIONS (Topic, Question, Choice_A, Choice_B, Choice_C, Choice_D, Answer, Difficulty, Points) VALUES ('Test', 'What is the answer to question 2?', 'A', 'B', 'C', 'D', 'Answer 2', 'Medium', '50.00')''')
        cursor.execute('''INSERT INTO QUESTIONS (Topic, Question, Choice_A, Choice_B, Choice_C, Choice_D, Answer, Difficulty, Points) VALUES ('Test', 'What is the answer to question 3?', 'A', 'B', 'C', 'D', 'Answer 3', 'Hard', '75.00')''')
        print("* Questions loaded into database table.")

        cursor.close()
    except sqlite3.Error as error:
        print('Error occurred - ', error)

def get_questions():
    try:
        cursor = dbconnection.cursor()

        get_questions = 'SELECT * FROM QUESTIONS;'
        cursor.execute(get_questions)

        questions = cursor.fetchall()
        print('\nQuestions:')
        for q in questions:
            print(q)
        print()

        cursor.close()
    except sqlite3.Error as error:
        print('Error occurred - ', error)
    finally:
        if dbconnection:
            dbconnection.close()

if __name__ == "__main__":
    start_server(HOST, PORT)