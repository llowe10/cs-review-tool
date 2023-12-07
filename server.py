# tutorial: https://codesource.io/creating-python-socket-server-with-multiple-clients/
# chat room project: https://github.com/IamLucif3r/Chat-On

import socket
from _thread import *
import random
import sqlite3
import time

HOST = '127.0.0.1'
PORT = 1891
QUESTION_LIMIT = 10
DATABASE_NAME = 'game.db'

clients = [] # [client objects]
usernames = [] # [client usernames]
dbconnection = sqlite3.connect(DATABASE_NAME, check_same_thread = False)

topics = [] # [game topics]
games = {} # {game ID: topic}
gameRooms = {} # {game ID: [client objects for each player]}
gamesInSession = [] # [game IDs for games currently in session]
scores = {} # {player username: score}
responseQueue = [] # [(player username, response)]

class Client:
    def __init__(self, conn, addr, username):
        self.conn = conn
        self.addr = addr
        self.username = username
        self.gameID = None
    
    def getConnection(self):
        return self.conn
    
    def getUsername(self):
        return self.username

    def setGameID(self, gameID):
        self.gameID = gameID
    
    def getGameID(self):
        return self.gameID

def play_game(player: Client):
    responseMutex = allocate_lock()
    confirmationMutex = allocate_lock()
    connection = player.getConnection()
    username = player.getUsername()
    gameID = player.getGameID()

    # wait until game has started
    while gameID not in gamesInSession:
        time.sleep(0.1)

    # game has started
    while gameID in gamesInSession:
        while responseMutex.locked():
            time.sleep(0.1)
        
        # get responses from player (one player at a time)
        responseMutex.acquire()
        connection.sendall(str.encode("What's your answer?"))
        response = connection.recv(2048).decode('utf-8')
        responseQueue.append((username, response))
        responseMutex.release()

        # check if player wants to continue
        confirmationMutex.acquire()
        connection.sendall(str.encode("Do you want to continue?"))
        confirmation = connection.recv(2048).decode('utf-8')
        if confirmation != 'Y':
            player.setGameID(None)
            gameRooms[gameID].remove(player)
            del scores[username]
        confirmationMutex.release()

def join_game(player: Client, games: dict):
    connection = player.getConnection()

    if len(games) == 0:
        connection.sendall(str.encode("No current games available."))
        clients.remove(player)
    else:
        # list all available game session IDs and topics
        availGames = ""
        for id in games:
            # ensure that games only contains games not in session
            if id not in gamesInSession:
                availGames += (str(id) + " -- " + games[id] + "\n")
            else:
                del games[id]
        connection.sendall(str.encode(f'\nAvailable games:\n{availGames}'))

        # capture game session ID
        while True:
            id = int(connection.recv(2048).decode('utf-8'))
            if id not in games:
                connection.sendall(str.encode(f'Game {id} does not exist.\n'))
            else:
                connection.sendall(str.encode(f'Joining game {id}...\n'))
                gameRooms[id].append(player)
                break
        
        play_game(player)

def get_scoreboard():
    # sort scoreboard from highest to lowest score
    rankings = sorted(scores.items(), key = lambda x: x[1], reverse = True)
    
    scoreboard = "\n"
    scoreboard += "SCOREBOARD".center(30, " ")
    scoreboard += "\nPLAYER".ljust(15, " ")
    scoreboard += "SCORE".rjust(15, " ")
    scoreboard += "\n"

    rank = 1
    for tup in rankings:
        result = "{:<10} {:>15}".format(tup[0], tup[1])
        scoreboard += (str(rank) + ". " + result + "\n")
        rank += 1
    
    return scoreboard

def administrate_game(admin: Client):
    try:
        cursor = dbconnection.cursor()
        gameID = admin.getGameID()
        adminConn = admin.getConnection()

        # initalize all player scores to 0
        playersList: Client = gameRooms[gameID]
        for i in range(len(playersList)):
            player: Client = playersList[i]
            username = player.getUsername()
            scores[username] = 0
        
        # get game content
        questions = []
        answerChoices = []
        correctAnswers = []
        points = []
        topic = games[gameID]
        query = f"""SELECT
                Question, Choice_A, Choice_B, Choice_C, Choice_D, Answer, Points
                FROM QUESTIONS WHERE Topic = \'{topic}\';"""
        cursor.execute(query)
        result = cursor.fetchall()
        for tup in result:
            questions.append(tup[0])
            answerChoices.append(tup[1] + "\n" + tup[2] + "\n" + tup[3] + "\n" + tup[4] + "\n")
            correctAnswers.append(tup[5])
            points.append(float(tup[6]))
        
        # game now in session
        gamesInSession.append(gameID)
        del games[gameID]
        
        # send out game content to players
        for i in range(0, QUESTION_LIMIT):
            if i >= len(questions): # delete later
                break

            question = questions[i]
            choices = answerChoices[i]
            answer = correctAnswers[i]
            pts = points[i]

            # send update to admin
            adminConn.sendall(str.encode(f'\nQuestion {i+1}: ' + question))

            # broadcast question and answer choices
            for j in range(len(playersList)):
                player: Client = playersList[j]
                playerConn = player.getConnection()
                playerConn.sendall(str.encode(f'\nQuestion {i+1}: ' + question + f"\n{choices}"))
            
            # wait for responses
            adminConn.sendall(str.encode("Waiting for responses..."))
            time.sleep(30)

            # get question responses from players
            for j in range(len(playersList)):
                player: Client = playersList[j]
                username = player.getUsername()
                playerConn = player.getConnection()

                responseMutex = allocate_lock()
                responseMutex.acquire()
                response = playerConn.recv(2048).decode('utf-8')
                responseQueue.append((username, response))
                responseMutex.release()

            # bonus given to first 3 players to respond correctly
            bonusGiven = 0
            for tup in responseQueue:
                if tup[1] == answer:
                    scores[tup[0]] += pts

                    if bonusGiven < 3:
                        if bonusGiven == 0:
                            scores[tup[0]] += 100
                        elif bonusGiven == 1:
                            scores[tup[0]] += 75
                        else:
                            scores[tup[0]] += 50
                        bonusGiven += 1
            
            # broadcast correct answer and scoreboard
            for i in range(len(playersList)):
                player: Client = playersList[i]
                playerConn = player.getConnection()

                playerConn.sendall(str.encode(f"{answer}" + "\n" + get_scoreboard()))
                confirmation = playerConn.recv(2048).decode('utf-8')

                # check if player wants to continue
                confirmationMutex = allocate_lock()
                confirmationMutex.acquire()
                if confirmation != 'Y':
                    # TODO: account for users leaving the game
                    # player.setGameID(None)
                    # gameRooms[gameID].remove(player)
                    # del scores[username]
                    playerConn.sendall(str.encode("\nLeaving game server. Thanks for playing!"))
                confirmationMutex.release()

        # determine what to do once game ends
        for i in range(len(playersList)):
            player: Client = playersList[i]
            playerConn = player.getConnection()

            playerConn.sendall(str.encode("\nGAME OVER. How do you wish to proceed?"))
            next_step = playerConn.recv(2048).decode('utf-8')
            
            if next_step.startswith("1"):
                playerConn.sendall(str.encode(f"\nRestarting game {gameID}..."))
                # TODO: add functionality to restart game
            elif next_step.startswith("2"):
                playerConn.sendall(str.encode(f"\nChoose a new game to join..."))
                # TODO: add functionality to join a new game
            else:
                playerConn.sendall(str.encode("\nLeaving game server. Thanks for playing!"))

        adminConn.sendall(str.encode("GAME OVER."))        
        cursor.close()
    except sqlite3.Error as error:
        print("Error occurred -", error)

def create_game(client: Client):
    try:
        cursor = dbconnection.cursor()
        connection = client.getConnection()

        # get available topics
        cursor.execute("SELECT DISTINCT Topic FROM QUESTIONS;")
        result = cursor.fetchall()
        for tup in result:
            topics.append(tup[0])
        
        # list available game topics to client
        avail_topics = ""
        for top in topics:
            avail_topics += ("-> " + top + "\n")
        connection.sendall(str.encode(f'\nAvailable topics:\n{avail_topics}'))

        # capture game topic from client
        while True:
            topic = connection.recv(2048).decode('utf-8')
            if topic not in topics:
                connection.sendall(str.encode(f'Topic \'{topic}\' does not exist.\n'))
            else:
                break
        
        # randomly generate session ID
        while True:
            id = random.randint(1000, 9999)
            if id not in games:
                games[id] = topic
                connection.sendall(str.encode(f'New game created! Session ID: {id}\n'))
                gameRooms[id] = []
                client.setGameID(id)
                break
        
        # start game once administrator confirms
        connection.sendall(str.encode(f'Waiting for players to join...'))
        confirmation = connection.recv(2048).decode('utf-8')
        if confirmation == 'Y':
            administrate_game(client)
        
        cursor.close()
    except sqlite3.Error as error:
        print("Error occurred -", error)

def client_handler(connection, address):
    client = None

    # get player username
    while True:
        username = connection.recv(2048).decode('utf-8')
        if username not in usernames:
            connection.sendall(str.encode(f'Welcome to CS Review Tool, {username}!\n'))
            client = Client(connection, address, username)
            clients.append(client)
            break
        else:
            connection.sendall(str.encode(f'User {username} already exists.'))
    
    # determine if player wants to create game or join game
    choice = connection.recv(2048).decode('utf-8')
    if choice == 'C':
        create_game(client)
    else:
        join_game(client, games)
    
    connection.close()

def accept_connections(ss):
    client, address = ss.accept()
    print("Connected to: " + address[0] + ":" + str(address[1]))
    start_new_thread(client_handler, (client, address, ))

def start_server(HOST, PORT):
    ss = socket.socket()
    try:
        ss.bind((HOST, PORT))
    except socket.error as e:
        print(str(e))
    
    print(f'Server is listening on port {PORT}...')
    ss.listen()

    load_questions()

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

        # Processes
        cursor.execute('''INSERT INTO QUESTIONS (Topic, Question, Choice_A, Choice_B, Choice_C, Choice_D, Answer, Difficulty, Points) VALUES ('Processes', 'Which scheduler is invoked frequently and must be fast?', 'A) Short-term / CPU', 'B) Medium-term', 'C) Long-term / Job', 'D) Process', 'A', 'Easy', '25.00')''')
        cursor.execute('''INSERT INTO QUESTIONS (Topic, Question, Choice_A, Choice_B, Choice_C, Choice_D, Answer, Difficulty, Points) VALUES ('Processes', 'What is a socket?', 'A) A program in execution', 'B) Information associated with a process', 'C) An endpoint for communication', 'D) Something to identify and manage a process', 'C', 'Medium', '50.00')''')
        # Memory Management
        cursor.execute('''INSERT INTO QUESTIONS (Topic, Question, Choice_A, Choice_B, Choice_C, Choice_D, Answer, Difficulty, Points) VALUES ('Memory Management', 'Which storage allocation scheme refers to allocating the smallest hole that is big enough for a process to be stored?', 'A) First-fit', 'B) Best-fit', 'C) Worst-fit', 'D) Segmentation', 'B', 'Medium', '50.00')''')
        # Intro to OS
        cursor.execute('''INSERT INTO QUESTIONS (Topic, Question, Choice_A, Choice_B, Choice_C, Choice_D, Answer, Difficulty, Points) VALUES ('Operating Systems', 'Why is direct memory access important?', 'A) It allows I/O devices to transmit at higher speeds', 'B) It is used to transfer data to secondary memory', 'C) It serves as a secondary cache', 'D) It is necessary for addressing interrupts', 'A', 'Hard', '75.00')''')
        print("* Questions loaded into database table.")

        cursor.close()
    except sqlite3.Error as error:
        print('Error occurred - ', error)

if __name__ == "__main__":
    start_server(HOST, PORT)