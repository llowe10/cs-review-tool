# tutorial: https://codesource.io/creating-python-socket-server-with-multiple-clients/
# chat room project: https://github.com/IamLucif3r/Chat-On

import socket
from _thread import *
import random

HOST = '127.0.0.1'
PORT = 1891
QUESTION_LIMIT = 10

clients = []
usernames = []
topics = []

sessions = {} # {game ID: topic}
gameRooms = {} # {game ID: [player connections]}

scores = {} # (player username: score)
responseQueue = [] # (connection, response)

def join_game(connection):
    # list all available game session IDs and topics
    avail_sess = ""
    for id in sessions:
        avail_sess += (str(id) + " -- " + sessions[id] + "\n")
    connection.sendall(str.encode(f'Available games:\n{avail_sess}'))

    # capture game session ID from client
    id = None
    while True:
        id = int(connection.recv(2048).decode('utf-8'))
        if id not in sessions:
            connection.sendall(str.encode(f'Game {id} does not exist.\n'))
        else:
            connection.sendall(str.encode(f'Joining game {id}...\n'))
            gameRooms[id].append(connection)
            break

def create_game(connection):
    # TODO: get available topics from database
    topics.append('TBD')

    # list available game topics to client
    avail_top = ""
    for top in topics:
        avail_top += (top + "\n")
    connection.sendall(str.encode(f'Available topics:\n{avail_top}'))

    # capture game topic from client
    topic = None
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
    
    # TODO: send out questions to users in game room
    for i in range(QUESTION_LIMIT):
        # broadcast question to users

        correctAnswer = None # get answer from database
        answerPoints = -1 # get points from database

        bonusGiven = 0 # bonus given to first 3 players to respond correctly
        for tup in responseQueue:
            if tup[1] == correctAnswer:
                scores[tup[0]] += answerPoints

                if bonusGiven < 3:
                    if bonusGiven == 0:
                        scores[tup[0]] += 100
                    elif bonusGiven == 1:
                        scores[tup[0]] += 75
                    else:
                        scores[tup[0]] += 50
                    bonusGiven += 1
        
        # broadcast correct answer to players

        # broadcast scoreboard to players
        break

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

    while True:
        accept_connections(ss)

if __name__ == "__main__":
    start_server(HOST, PORT)