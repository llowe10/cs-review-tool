# tutorial: https://codesource.io/creating-python-socket-server-with-multiple-clients/
# chat room project: https://github.com/IamLucif3r/Chat-On

import socket
import time

HOST = '127.0.0.1'
PORT = 1891

def player(client):
    while True:
        # print question and answer choices
        question = client.recv(2048).decode('utf-8')
        print(question)
        if question == "GAME OVER":
            break
        print(client.recv(2048).decode('utf-8'))

        # submit answer choice
        #update = client.recv(2048).decode('utf-8')
        #while update == "Waiting...":
        #    update = client.recv(2048).decode('utf-8')
        choice = input("Enter your answer: ")
        client.send(str.encode(choice))
        print(client.recv(2048).decode('utf-8'))

        # print answer and scoreboard
        print(client.recv(2048).decode('utf-8')) 
        print(client.recv(2048).decode('utf-8'))

        # confirm if player wants to continue
        response = input("Enter 'Y' to continue: ")
        if response != 'Y':
            break

def administrator(client):
    # waiting for game to start
    print(client.recv(2048).decode('utf-8'))
    time.sleep(30)
    response = input("Enter 'Y' to start the game: ")
    client.send(str.encode(response))

    # sending updates as game progresses
    while True:
        update = client.recv(2048).decode('utf-8')
        print(update)
        if update.startswith("GAME"):
            break
        else:
            update = client.recv(2048).decode('utf-8')
            print(update)

def start_client(HOST, PORT):
    client = socket.socket()
    print("Waiting for connection...")

    try:
        client.connect((HOST, PORT))
    except socket.error as e:
        print(str(e))

    # prompt player for username
    while True:
        username = input("Enter username: ")
        client.send(str.encode(username))
        response = client.recv(2048).decode('utf-8')
        print(response)

        if response.startswith('Welcome'):
            break

    # prompt player to create or join game
    print("Do you want to create or join a game?")
    while True:
        choice = input("Enter C to create or J to join: ")
        if choice == 'C' or choice == 'J':
            client.send(str.encode(choice))
            response = client.recv(2048).decode('utf-8')
            print(response)

            if choice == 'C':
                while True:
                    topic = input("Choose a topic: ")
                    client.send(str.encode(topic))
                    response = client.recv(2048).decode('utf-8')
                    print(response)
                    if response.startswith('New game'):
                        administrator(client)
                        break
            else:
                if response.startswith("No current"):
                    break
                while True:
                    id = input("Choose a game ID: ")
                    client.send(str.encode(str(id)))
                    response = client.recv(2048).decode('utf-8')
                    print(response)
                    if response.startswith('Joining'):
                        player(client)
                        break
            break
        else:
            print("Invalid input.\n")

    client.close()

if __name__ == "__main__":
    start_client(HOST, PORT)