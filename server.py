# tutorial: https://codesource.io/creating-python-socket-server-with-multiple-clients/
# chat room project: https://github.com/IamLucif3r/Chat-On

import socket
from _thread import *
import random
import sqlite3

HOST = '127.0.0.1'
PORT = 1891
DATABASE_NAME = 'game.db'

clients = []
usernames = []
sessions = []
dbconnection = sqlite3.connect(DATABASE_NAME)

def join_game(connection):
    # list all available game session IDs
    avail_sess = ""
    for id in sessions:
        avail_sess += (str(id) + "\n")
    
    connection.sendall(str.encode(f'Available games:\n{avail_sess}'))

def create_game(connection):
    # randomly generate session ID
    while True:
        id = random.randint(1000, 9999)
        if id not in sessions:
            sessions.append(id)
            break
    
    connection.sendall(str.encode(f'New game created! Session ID: {id}\n'))

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
        join_game(connection)
    
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
    get_questions()

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

        cursor.close()
    except sqlite3.Error as error:
        print('Error occurred - ', error)
    finally:
        if dbconnection:
            dbconnection.close()

if __name__ == "__main__":
    start_server(HOST, PORT)