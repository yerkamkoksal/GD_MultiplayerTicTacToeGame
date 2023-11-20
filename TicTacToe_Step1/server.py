import socket
import threading
import tkinter as tk
import time

class TicTacToeGame: #This class is responsible for the game logic.
    def __init__(self, players):
        self.players = players #players is a dictionary of the form {username: (client_socket, symbol)}
        self.board = {str(i): str(i) for i in range(1, 10)} #board is a dictionary of the form {cell: symbol}
        self.turn = 'X' #turn is either 'X' or 'O'

    def make_move(self, cell, symbol): #This function is called when a player makes a move.
        valid_move = True #valid_move is a boolean that is True if the move is valid and False otherwise.
        game_status = ["continue", None, None] #game_status is a list of the form [status, result, opponent_result]


        if 1 <= cell <= 9 and self.board[str(cell)].isdigit(): #If the cell is valid and empty.
            self.board[str(cell)] = symbol #Set the cell to the player's symbol.
            self.broadcast_board() #Broadcast the board to all players.

            if self.check_win(symbol): #If the player won.
                game_status = ["end", "win", "loss"] #Set the game status to end, win, loss.
            elif self.check_draw(): #If the game is a draw.
                game_status = ["end", "draw", "draw"] #Set the game status to end, draw, draw.
            else: #If the game is not over.
                self.turn = 'O' if self.turn == 'X' else 'X' #Change the turn to the other player.
                valid_move = True #Set valid_move to True.
        else:
            return False, game_status

        return valid_move, game_status


    def check_win(self, symbol): #This function checks if the player with the given symbol won.
        win_combinations = [ #win_combinations is a list of all possible win combinations.
            ('1', '2', '3'), ('4', '5', '6'), ('7', '8', '9'),
            ('1', '4', '7'), ('2', '5', '8'), ('3', '6', '9'),
            ('1', '5', '9'), ('3', '5', '7')
        ]
        for a, b, c in win_combinations:
            if self.board[a] == self.board[b] == self.board[c] == symbol: #If the player has a winning combination.
                return True
        return False

    def check_draw(self): #This function checks if the game is a draw.
        for cell in self.board.values(): #For each cell in the board.
            if cell.isdigit():  #If the cell is empty.
                return False
        return True

    def broadcast_board(self): #This function broadcasts the board to all players.
        board_repr = self.board_repr() #board_repr is a string representation of the board.
        for _, (client_socket, _) in self.players.items(): #For each player.
            client_socket.send(f"BOARD {board_repr}".encode()) #Send the board to the player.

    def board_repr(self): #This function returns a string representation of the board.
        board_repr = ''
        for i in range(1, 10):
            board_repr += f"{self.board[str(i)]}" 
            if i % 3 != 0: 
                board_repr += "|" 
            elif i != 9:
                board_repr += "\n"
        return board_repr

    def get_opponent_username(self, username): #This function returns the opponent's username.
        for opponent_username, (_, player_symbol) in self.players.items():
            if opponent_username != username:
                return opponent_username



class Server: #This class is responsible for the server GUI and client handling.
    def __init__(self, host):
        self.players_ready = [] #players_ready is a list of players that are ready to play.
        self.host = host #host is the server's IP address.
        self.port = None #port is the server's port.
        self.server_socket = None #server_socket is the server's socket.
        self.clients = {} #clients is a dictionary of the form {username: (client_socket, client_address)}

        self.root = tk.Tk()
        self.root.title("Server")
        self.root.geometry("500x600")

        self.status_label = tk.Label(self.root, text="Server is not running", fg="red")
        self.status_label.pack()

        self.ip_label = tk.Label(self.root, text="Host: " + self.host)
        self.ip_label.pack()

        self.log_text = tk.Text(self.root, width=40, height=15) #log_text is a text widget that displays the server's logs.
        self.log_text.pack()

        self.port_label = tk.Label(self.root, text="Port:")
        self.port_label.pack()
        self.port_entry = tk.Entry(self.root) #port_entry is an entry widget that allows the user to enter the server's port.
        self.port_entry.pack()
        self.start_button = tk.Button(self.root, text="Start Server", command=self.start_server)
        self.start_button.pack()

        self.stop_button = tk.Button(self.root, text="Stop Server", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.pack()

        self.board_frame = tk.Frame(self.root)
        self.board_frame.pack()
        self.board_label = tk.Label(self.board_frame, text="Board:")
        self.board_label.pack()
        self.board_text = tk.Text(self.board_frame, width=20, height=10) #board_text is a text widget that displays the board.
        self.board_text.pack()
        self.board_text.config(state="disabled")

        self.root.mainloop() #Start the GUI's main loop.

    def broadcast(self, message): #This function broadcasts a message to all players.
        for username, (client_socket, client_address) in self.clients.items():
            client_socket.send(f"MESSAGE {message}".encode())

    def update_server_board(self): #This function updates the board in the GUI after each move and initialization.
        self.board_text.config(state="normal")
        self.board_text.delete("1.0", tk.END)
        self.board_text.insert(tk.END, "Board:\n\n")
        self.board_text.insert(tk.END, self.tic_tac_toe_game.board_repr())
        self.board_text.config(state="disabled")

    def start_server(self): #This function starts the server. It is called when the user clicks the start server button.
        self.port = int(self.port_entry.get()) #Get the port from the port entry.

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Create a TCP socket.
        self.server_socket.bind((self.host, self.port)) #Bind the socket to the host and port.
        self.server_socket.listen() #Listen for incoming connections.
        self.log_text.insert(tk.END, "Listening on port: " + str(self.port) + "\n") #Log the port.

        self.status_label.config(text="Server is running", fg="green")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        self.listening = True #listening is a boolean that is True if the server is listening for incoming connections and False otherwise.

        client_thread = threading.Thread(target=self.receive) #Create a thread for receiving incoming connections.
        client_thread.start()

    def start_game(self): #This function starts the game. It is called when two players are ready to play.
        symbols = ['X', 'O']
        players = {} #players is a dictionary of the form {username: (client_socket, symbol)}
        for i, username in enumerate(self.players_ready): #For each player.
            client_socket, client_address = self.clients[username] #Get the player's socket and address.
            symbol = symbols[i] #Get the player's symbol.
            client_socket.send(f"SYMBOL {symbol}".encode()) #Send the player their symbol.
            self.log_text.insert(tk.END, f"{username} is appointed {symbol}\n") #Log the player's symbol.
            players[username] = (client_socket, symbol) #Add the player to the players dictionary.

        self.tic_tac_toe_game = TicTacToeGame(players) #Create a TicTacToeGame object.

        self.tic_tac_toe_game.broadcast_board() #Broadcast the board to all players.
        self.update_server_board() #Update the board in the GUI.

        first_player = self.players_ready[0] #Get the first player.
        first_player_socket = self.clients[first_player][0] #Get the first player's socket.
        first_player_socket.send(f"YOUR_TURN".encode()) #Send the first player a YOUR_TURN message.
        self.log_text.insert(tk.END, f"It's {first_player}'s turn\n") #Log the first player's turn. 

        second_player = self.players_ready[1] #Get the second player.
        second_player_socket = self.clients[second_player][0] #Get the second player's socket. 
        second_player_socket.send(f"OPPONENT_TURN".encode()) #Send the second player an OPPONENT_TURN message.

    def receive(self): #This function is called when the server is listening for incoming connections.
        while self.listening: 
            try:
                client_socket, client_address = self.server_socket.accept() #Accept an incoming connection.
                username = client_socket.recv(1024).decode() #Receive the username from the client.
                if username in self.clients: #If the username is already taken.
                    client_socket.send("Username already taken".encode()) #Send the client a message.
                    client_socket.close() #Close the client's socket.
                    continue
                else:
                    self.clients[username] = (client_socket, client_address) #Add the client to the clients dictionary.
                    client_socket.send("Connected to the server".encode()) #Send the client a message.
                    self.log_text.insert(tk.END, f"{username} connected\n") #Log the connection.
                    self.players_ready.append(username) #Add the player to the players_ready list.

                    client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address, username)) #Create a thread for handling the client.
                    client_thread.start()

                if len(self.players_ready) == 2: #If there are two players ready to play.
                    self.start_game() #Start the game.

            except socket.error: 
                if self.listening:
                    self.log_text.insert(tk.END, "Error: Connection lost\n")
                break


    def handle_client(self, client_socket, client_address, username): #This function is called when a client is connected.
        while True: #While the client is connected.
            try:
                data = client_socket.recv(1024).decode() #Receive data from the client.

                if not data: #If the data is empty.
                    break

                if data.startswith('MOVE'): #If the data is a MOVE message.
                    cell = int(data[-1]) #Get the cell from the data.
                    symbol = self.tic_tac_toe_game.players[username][1] #Get the player's symbol.
                    valid_move, game_status = self.tic_tac_toe_game.make_move(cell, symbol) #Make a move.
                    self.update_server_board() #Update the board in the GUI.

                    if valid_move: #If the move is valid.
                        client_socket.send("VALID_MOVE".encode()) #Send the client a VALID_MOVE message.
                        self.log_text.insert(tk.END, f"VALID_MOVE message sent to {username}\n") #Log the message.
                        self.log_text.insert(tk.END, f"{username} made a move at cell {cell}\n") #Log the move.
                        self.log_text.insert(tk.END, f"Game status: {game_status}\n") #Log the game status.

                        if game_status[0] == "end" and game_status[1] == "win": #If the game is over and the player won.
                            client_socket.send(f"WIN".encode()) #Send the client a WIN message.
                            opponent_username = self.tic_tac_toe_game.get_opponent_username(username)
                            opponent_client_socket, _ = self.tic_tac_toe_game.players[opponent_username]
                            opponent_client_socket.send(f"LOSS".encode()) #Send the opponent a LOSS message.
                            self.log_text.insert(tk.END, f"{username} won!\n") #Log the win.
                            client_socket.send(f"WIN".encode()) #Send the client a WIN message.
                            break
                        elif game_status[0] == "end" and game_status[1] == "draw": #If the game is over and the game is a draw.
                            opponent_username = self.tic_tac_toe_game.get_opponent_username(username)
                            opponent_client_socket, _ = self.tic_tac_toe_game.players[opponent_username]
                            opponent_client_socket.send(f"DRAW".encode()) #Send the opponent a DRAW message.
                            client_socket.send(f"DRAW".encode()) #Send the client a DRAW message.
                            self.log_text.insert(tk.END, f"It's a draw.\n") #Log the draw. 
                            break
                        elif game_status[0] == "continue": #If the game is not over.
                            if self.tic_tac_toe_game.turn == symbol: #If it's the player's turn.
                                client_socket.send(f"YOUR_TURN".encode()) #Send the client a YOUR_TURN message.
                                self.log_text.insert(tk.END, f"It's {username}'s turn\n")
                                opponent_username = self.tic_tac_toe_game.get_opponent_username(username)
                                opponent_client_socket, _ = self.tic_tac_toe_game.players[opponent_username]
                                opponent_client_socket.send(f"OPPONENT_TURN".encode()) #Send the opponent an OPPONENT_TURN message.

                            else: #If it's the opponent's turn.
                                client_socket.send(f"OPPONENT_TURN".encode()) #Send the client an OPPONENT_TURN message.
                                opponent_username = self.tic_tac_toe_game.get_opponent_username(username)
                                opponent_client_socket, _ = self.tic_tac_toe_game.players[opponent_username]
                                self.log_text.insert(tk.END, f"It's {opponent_username}'s turn\n")
                                opponent_client_socket.send(f"YOUR_TURN".encode()) #Send the opponent a YOUR_TURN message.


                    else:
                        client_socket.send(f"INVALID_MOVE".encode()) #Send the client an INVALID_MOVE message.
                        self.log_text.insert(tk.END, f"INVALID_MOVE message sent to {username}\n") #Log the message.
                else:
                    self.log_text.insert(tk.END, f"{username}: {data}\n") #Log the message.
            except socket.error:
                del self.clients[username]
                self.players_ready.remove(username)

    
    def stop_server(self): #This function stops the server. It is called when the user clicks the stop server button.
        self.listening = False
        self.server_socket.close()
        self.log_text.insert(tk.END, f"Server stopped\n")
        self.status_label.config(text="Server is not running", fg="red")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

if __name__ == "__main__": #If the script is run directly.
    host = socket.gethostbyname(socket.gethostname()) #Get the host's IP address.
    server = Server(host) #Create a Server object.