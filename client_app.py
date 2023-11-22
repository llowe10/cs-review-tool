# tutorial: https://codesource.io/creating-python-socket-server-with-multiple-clients/
# chat room project: https://github.com/IamLucif3r/Chat-On

import socket

class Client():
    def __init__(self) -> None:
        self.client = socket.socket()

    def start_client(self, HOST, PORT):
        print("Waiting for connection...")
        try:
            self.client.connect((HOST, PORT))
        except socket.error as e:
            print(str(e))
        # return self.client

    def set_username(self):
        # prompt player for username
        while True:
            username = input("Enter username: ")
            self.client.send(str.encode(username))
            response = self.client.recv(2048).decode('utf-8')
            print(response)

            if response.startswith('Welcome'):
                return response
                # break

    def options(self):
        # prompt player to create or join game
        print("Do you want to create or join a game?")
        while True:
            choice = input("Enter C to create or J to join: ")
            if choice == 'C' or choice == 'J':
                self.client.send(str.encode(choice))
                response = self.client.recv(2048).decode('utf-8')
                print(response)
                return response
                # break
            else:
                print("Invalid input.\n")

    def close(self):
        self.client.close()

# if __name__ == "__main__":
#     start_client(HOST, PORT)
#     set_username()
#     options()
#     close()