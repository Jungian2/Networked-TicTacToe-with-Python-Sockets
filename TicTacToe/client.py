import socket
import time
from caesarcipher import *

hostname = socket.gethostname()

# Host and port information needed to join the server
host = socket.gethostbyname(hostname)
port = 8080

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Creates client socket object

cipher = CaesarCipher()  # Create an instance of the CaesarCipher class


class Client:

    @staticmethod
    def print_matrix(matrix):
        """ prints the matrix for both players"""
        print("  0   1   2 ")
        for i in range(3):
            for j in range(3):  # These two for loops (i) and (j) creates the 3x3 matrix
                current = "-"
                if matrix[i][j] == 1:  # if an entry in the matrix is equal to 1 then set that to "X"
                    current = "X"
                elif matrix[i][j] == 2:  # else if an entry in the matrix is equal to 2 then set that to "O"
                    current = "O"
                print("|", current, end=" ")
            print(f"| {i} ")

    def connect_player(self):
        """ Connects the client to the server and calls the starts the game function"""
        try:
            client.connect((host, port))
            print(f"Connected to: [HOST] {host} : [PORT] {port}")
            self.start_game()
            client.close()

        except socket.error as e:
            print("Connection error: ", e)

    def start_game(self):
        # receiving, decoding & decrypting of the random shift value from the server
        shift_recv = client.recv(1024).decode("ascii")
        shift_decrypt = cipher.decrypt(0, shift_recv)

        # When the client receives the shift value from the server, set the empty variable
        # shift_value to be equal to the decrypted server value
        shift_value = shift_decrypt

        welcome = client.recv(1024).decode("ascii")
        welcome_decrypt = cipher.decrypt(shift_value, welcome)
        print(welcome_decrypt)

        print("--------------")
        print("| Scoreboard |")
        print("--------------")

        f = open("Scoreboard.txt", "r")
        content = f.read()
        print(content)
        f.close()

        # If the name is null or doesn't meet the requirements. Then it
        # enters an infinite loop until the conditions are met then the
        # loop is broken and the name is sent to the server
        name = input("Enter your name:")
        while True:
            if name == " " or len(name) > 10 or name == "":
                name = input("Enter a valid name:")
            else:
                break
        client.send(cipher.encrypt(0, name).encode("ascii"))

        # Client receives their name back from the server, as well as if they're player 1 or 2
        recv_name = client.recv(1024).decode("ascii")
        recv_name_decoded = cipher.decrypt(shift_value, recv_name)
        print(recv_name_decoded)

        while True:
            try:
                # Receiving the message from the server for whose turn it is
                recv_data = client.recv(2048 * 10).decode("ascii")
                recv_data_decoded = cipher.decrypt(shift_value, recv_data)

                # If the client receives input then they are prompted to enter a set of
                # coordinates whilst the other player has to wait until they have done so
                if recv_data_decoded == "Input":
                    failed = 1
                    while failed:
                        try:
                            x = int(input("Enter the x coordinate (row):"))
                            y = int(input("Enter the y coordinate (column):"))

                            # Appends both the x and y coordinates to a variable, seperated by a ","
                            # This "," will then be used to split the two values server side
                            coordinates = str(x) + "," + str(y)
                            client.send(cipher.encrypt(shift_value, coordinates).encode("ascii"))
                            failed = 0
                        except ValueError as e:
                            print("Error occurred...Try again", e)

                # If the server sends back an error, it will be sent to the client
                # along with a description of the cause of the error
                elif recv_data_decoded == "Error":
                    print("Coordinates out of bounds! Try again")

                elif recv_data_decoded == "Error already entered":
                    print("Already entered! Try again")

                # If the clients receive "Matrix" from the server, print the matrix
                # and fill the matrix using the coordinate values that both users
                # clients have provided. Which are then translated to X's or O's
                elif recv_data_decoded == "Matrix":
                    matrix_recv = client.recv(2048 * 100).decode("ascii")
                    matrix_recv_decoded = cipher.decrypt(shift_value, matrix_recv)
                    self.print_matrix(eval(matrix_recv_decoded))

                elif recv_data_decoded == "":
                    time.sleep(10)
                    break

                elif recv_data_decoded == "Rematch":
                    rematch = input("Do u want a rematch?:")
                    client.send(cipher.encrypt(shift_value, rematch).encode("ascii"))

                else:
                    print(recv_data_decoded)

            except KeyboardInterrupt:
                print("\nKeyboard Interrupt")
                time.sleep(1)
                break


game = Client()
game.connect_player()
