import socket
import time
from caesarcipher import *
import random

hostname = socket.gethostname()
host = socket.gethostbyname(hostname)  # The servers IP address
print(host)
port = 8080
matrix = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]  # Matrix used to store values by both clients

player_one = 1
player_two = 2

player_connection = list()
player_address = list()
player_name = list()

# The random shift value is taken from the caesar_cipher.py and set equal to
# the empty value created in server.py
shift_value = random.randint(0, 38)

# Creates server socket object
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

cipher = CaesarCipher()  # Create an instance of the CaesarCipher class

score_board = {}
Rematch = list()


class Server:

    def start_server(self):
        """ initialises the server and begins listening for connections."""
        try:
            server.bind((host, port))
            print(f"Server started, Binding to port: {port}")
            server.listen(2)
            self.accept_player()
        except socket.error as e:
            print(f"Server binding error: {e}")

    def start_game(self):
        """Starts the game and continue whilst no one has won or drawn."""
        result = 0
        i = 0

        while result == 0 and i < 9:
            if i % 2 == 0:
                self.get_input(player_one)
            else:
                self.get_input(player_two)
            result = self.check_winner()
            i = i + 1

        if result == 1:  # If the result is equal to 1 broadcast to all players that player 1 has won
            last_message = f"{player_name[0]}! is the winner"
            score_board[player_name[0]] = score_board[player_name[0]] + 1

        elif result == 2:  # If the result is equal to 2 broadcast to all players that player 2 has won
            last_message = f"{player_name[1]}! is the winner"
            score_board[player_name[1]] = score_board[player_name[1]] + 1

        else:
            last_message = "Draw!!!"

        self.broadcast(last_message)

        print(score_board)

        self.rematch()

        # Once the game has finished go through each connection in the
        # connections list and close them

        """
        for conn in player_connection:
            conn.close()
        """

    def rematch(self):

        for i in range(2):
            player_connection[i].send(cipher.encrypt(shift_value, "Rematch").encode("ascii"))
            recv_answer = player_connection[i].recv(2048 * 10).decode("ascii")
            answer_decrypt = cipher.decrypt(shift_value, recv_answer)

            print(answer_decrypt)
            Rematch.append(answer_decrypt)

        Vote = Rematch.count("yes")
        if Vote == 2:
            rematch = True
        else:
            rematch = False

        if rematch:
            Rematch.clear()
            for i in range(0, 3):
                for j in range(0, 3):
                    matrix[i][j] = 0
            self.start_game()

        else:
            with open("Scoreboard.txt", 'a') as f:
                for key, value in score_board.items():
                    f.write('%s | Wins: %s\n' % (key, value))

            for conn in player_connection:
                conn.close()

    def accept_player(self):
        """ accepts two clients, receives clients details and then calls the start_game() function.
        When two clients are accepted, sends a welcome message to the client to let them know
        they have successfully joined the server. Then sends the caesar ciphers shift value to the client.
        Once received the client sends the encoded name to the server, its then decoded it and appended to
        its own list along with the connection and address.
        """
        try:
            welcome = "Welcome to the server"
            for i in range(2):
                print("Shift value:", shift_value)

                # accept connections from the client
                connection, address = server.accept()

                # Once we've accepted a client, we take the shift value variable:
                # encrypt -> encode -> send to the client

                connection.send(cipher.encrypt(0, str(shift_value)).encode("ascii"))

                # Test the shift value is correct by sending a message to the client
                # and having them decrypt it with the shift value we sent
                connection.send(cipher.encrypt(shift_value, welcome).encode("ascii"))

                # Receive the clients name and decrypt
                name_recv = connection.recv(2048 * 10).decode("ascii")
                name_decrypt = cipher.decrypt(0, name_recv)

                player_connection.append(connection)
                player_address.append(address)
                player_name.append(name_decrypt)
                score_board[name_decrypt] = 0

                print("Player {} - {} [{}:{}]".format(i + 1, name_decrypt, address[0], str(address[1])))

                # Send the client an encrypted message saying if they are player 1 or 2
                player_message = "Hi {}, you are player {}".format(name_decrypt, str(i + 1))
                connection.send(cipher.encrypt(shift_value, player_message).encode("ascii"))

            self.start_game()
            server.close()
        except socket.error as e:
            print("Player connection error", e)

    @staticmethod
    def validate_input(x, y, conn):
        """ Validates input when the client is entering the coordinates.
        Checks first that the user is entering coordinates within the scope
        of the 3x3 matrix and then checks the coordinates the user enters are
        not where an already entered 1 or 2 is (X or O).
        """

        if x > 3 or y > 3:
            print("\nOut of bounds! Enter again...")
            conn.send(cipher.encrypt(shift_value, "Error").encode("ascii"))
            return False
        elif matrix[x][y] != 0:
            print("\nAlready entered! Try again...\n")
            conn.send(cipher.encrypt(shift_value, "Error already entered").encode("ascii"))
            return False
        return True

    def get_input(self, currentPlayer):
        """ Gets input from the current player
        as well as setting different states for both players based off of whose turn it is.
        """

        # Send a message using the broadcast() function to both players saying whose turn it is
        if currentPlayer == player_one:
            player = f"{player_name[0]}'s turn"
            connection = player_connection[0]
        else:
            player = f"{player_name[1]}'s turn"
            connection = player_connection[1]
        print(player)
        self.broadcast(player)
        # Once the message has been sent, enter an infinite loop
        failed = 1
        while failed:
            try:
                # In this loop send the prompt to enter coordinates to whoever turn it is
                connection.send(cipher.encrypt(shift_value, "Input").encode("ascii"))

                # Once received decrypt these coordinates and split them
                data = connection.recv(2048 * 10).decode("ascii")
                data_decoded = cipher.decrypt(shift_value, data).split(",")
                print(data_decoded)

                # The two X and Y values from the client are appended into one variable client side then
                # split on the server side using the "," and set to there respective x and y variables
                x = int(data_decoded[0])
                y = int(data_decoded[1])

                # Validate them using the validation function
                if self.validate_input(x, y, connection):
                    matrix[x][y] = currentPlayer
                    failed = 0  # Exit the infinite loop
                    self.broadcast("Matrix")

                    self.broadcast(str(matrix))
            except ValueError as e:
                connection.send(cipher.encrypt(shift_value, "Error").encode("ascii"))
                print("Error occurred! Try again...", e)

    @staticmethod
    def broadcast(text):
        """ Sends messages to both players based upon their input and sends the matrix"""

        player_connection[0].send(cipher.encrypt(shift_value, text).encode("ascii"))
        player_connection[1].send(cipher.encrypt(shift_value, text).encode("ascii"))
        time.sleep(2)

    @staticmethod
    def check_rows():
        """ Game logic - checks rows in the matrix for the same values across a row in succession.
        If a row are all the same value (1 or 2), it sets the result to be equal
        to either 1 or 2, which corresponds to players 1 or 2
        """
        result = 0
        for i in range(3):
            if matrix[i][0] == matrix[i][1] and matrix[i][1] == matrix[i][2]:
                result = matrix[i][0]
                if result != 0:
                    break
        return result

    @staticmethod
    def check_columns():
        """ Game logic - checks the columns of the matrix for the same value in succession.
        If a column are all the same value (1 or 2), it sets the result to be equal
        to either 1 or 2, which corresponds to players 1 or 2
        """
        result = 0
        for i in range(3):
            if matrix[0][i] == matrix[1][i] and matrix[1][i] == matrix[2][i]:
                result = matrix[0][i]
                if result != 0:
                    break
        return result

    @staticmethod
    def check_diagonals():
        """ Game logic - checks diagonally across the matrix for the same value in succession.
        If a row are all the same value (1 or 2), it sets the result to be equal
        to either 1 or 2, which corresponds to players 1 or 2
        """
        result = 0
        if matrix[0][0] == matrix[1][1] and matrix[1][1] == matrix[2][2]:
            result = matrix[0][0]
        elif matrix[0][2] == matrix[1][1] and matrix[1][1] == matrix[2][0]:
            result = matrix[0][2]
        return result

    def check_winner(self):
        """ Checks each functions used to check for matching values in the matrix and returns a result.
        If one of the functions that check for matching values are null then move onto checking
        the next function, if the value is not null then stop and return the result (1 or 2)
        """
        result = self.check_rows()
        if result == 0:
            result = self.check_columns()
        if result == 0:
            result = self.check_diagonals()
        return result


game = Server()
game.start_server()
