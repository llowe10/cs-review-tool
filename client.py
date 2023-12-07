# tutorial: https://codesource.io/creating-python-socket-server-with-multiple-clients/
# chat room project: https://github.com/IamLucif3r/Chat-On

import socket
import time

HOST = '127.0.0.1'
PORT = 1891

def player(client):
    response = client.recv(2048).decode('utf-8')

    # while response != "GAME OVER":
    while True:
        # print question and answer choices
        print(response)
        print(client.recv(2048).decode('utf-8'))

        # submit answer choice
        choice = input("Enter your answer: ")
        client.send(str.encode(choice))
        
        # confirm if player wants to continue
        answer = client.recv(2048).decode('utf-8')
        print(f"Correct Answer: {answer}")

        message = client.recv(2048).decode('utf-8')
        print(f"{message}")

        # proceed = client.recv(2048).decode('utf-8')
        # print(f"\n{proceed}")
        if "GAME OVER" in message:
            break

        response = input("\nEnter 'Y' to continue: ")
        client.send(str.encode(response))

    proceed = input("\nEnter\n-> '1' to play again\n-> '2' to join a new game\n-> '3' to leave the server\n: ")
    client.send(str.encode(proceed))

def administrator(client):
    # waiting for game to start
    print(client.recv(2048).decode('utf-8'))
    time.sleep(30)
    response = input("Enter 'Y' to start the game: ")
    client.send(str.encode(response))

    # sending updates as game progresses
    while True:
        update = client.recv(2048).decode('utf-8')
        print(f"\n{update}")
        if update.startswith("GAME"):
            # next_step = client.recv(2048).decode('utf-8')
            # print(next_step)
            # response = input("Enter '1' to play again, '2' to join a new game, or '3' to leave the server: ")
            # client.send(str.encode(response))
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