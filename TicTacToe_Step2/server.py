import socket
import threading
import tkinter as tk
import tkinter.scrolledtext as st
import time
import random

class TicTacToeGame:
    def __init__(self, players, spectators):
        self.players = players
        self.spectators = spectators
        self.board = {str(i): str(i) for i in range(1, 10)}
        self.turn = 'X'
    
    def board_repr(self):
        board_repr = ''
        for i in range(1, 10):
            board_repr += f"{self.board[str(i)]}"
            if i % 3 != 0:
                board_repr += "|"
            elif i != 9:
                board_repr += "\n"
        return board_repr

    def broadcast_board(self):
        board_repr = self.board_repr()
        for _, (client_socket, _) in self.players.items():
            client_socket.send(f"BOARD {board_repr}".encode())
        for _, (client_socket,) in self.spectators.items():
            client_socket.send(f"BOARD {board_repr}".encode())

    def add_spectator(self, username, client_socket):
        self.spectators[username] = (client_socket,)
        self.broadcast_board()
        

    def make_move(self, cell, symbol):
        valid_move = True
        game_status = ["continue", None, None]

        if 1 <= cell <= 9 and self.board[str(cell)].isdigit():
            self.board[str(cell)] = symbol
            self.broadcast_board()

            winning_symbol = self.check_win()
            if winning_symbol:
                game_status = ["end", "win" if symbol == winning_symbol else "loss", winning_symbol]
            elif self.check_draw():
                game_status = ["end", "draw", "draw", None]
            else:
                self.turn = 'O' if self.turn == 'X' else 'X'
                valid_move = True
        else:
            return False, game_status

        return valid_move, game_status

    def check_win(self):
        win_combinations = [
            ('1', '2', '3'), ('4', '5', '6'), ('7', '8', '9'),
            ('1', '4', '7'), ('2', '5', '8'), ('3', '6', '9'),
            ('1', '5', '9'), ('3', '5', '7')
        ]
        for a, b, c in win_combinations:
            if self.board[a] == self.board[b] == self.board[c]:
                return self.board[a]
        return None

    def check_draw(self):
        for cell in self.board.values():
            if cell.isdigit():
                return False
        return True

    def get_opponent_username(self, username):
        for opponent_username, (_, player_symbol) in self.players.items():
            if opponent_username != username:
                return opponent_username


class Server:
    def __init__(self, host):

        self.clients = {}
        self.players = []
        self.spectators = []
        self.games_played = 0
        self.game = None

        self.root = tk.Tk()
        self.root.title("Server")
        self.root.geometry("800x450")

        self.upper_frame = tk.Frame(self.root)
        self.upper_frame.pack()

        self.host_label = tk.Label(self.upper_frame, text="Host:")
        self.host_label.pack(side="left")
        self.host_number = tk.Label(self.upper_frame, text=host)
        self.host_number.pack(side="left")

        self.port_label = tk.Label(self.upper_frame, text="Port:")
        self.port_label.pack(side="left")
        self.port_entry = tk.Entry(self.upper_frame)
        self.port_entry.pack(side="left")

        self.start_button = tk.Button(self.upper_frame, text="Start", command=self.start_server)
        self.start_button.pack(side="left")

        self.stop_button = tk.Button(self.upper_frame, text="Stop", command=self.stop_server, state="disabled")
        self.stop_button.pack(side="left")

        self.status_label = tk.Label(self.upper_frame, text="Server is not running", fg="red")
        self.status_label.pack(side="right")

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack()

        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side="left")

        self.logs_label = tk.Label(self.left_frame, text="Logs:")
        self.logs_label.pack()
        self.log_text_box = st.ScrolledText(self.left_frame, width=50, height=20)
        self.log_text_box.pack()

        self.games_label = tk.Label(self.left_frame, text="Total games played:")
        self.games_label.pack()

        self.games_text = tk.Text(self.left_frame, width=10, height=1)
        self.games_text.pack()
        self.games_text.config(state="disabled")

        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.pack(side="right")

        self.right_upper_frame = tk.Frame(self.right_frame)
        self.right_upper_frame.pack(side="top")

        self.main_left_frame = tk.Frame(self.right_upper_frame)
        self.main_left_frame.pack(side="left")
        self.players_label = tk.Label(self.main_left_frame, text="Players:")
        self.players_label.pack()
        self.players_listbox = tk.Listbox(self.main_left_frame)
        self.players_listbox.pack()

        self.main_right_frame = tk.Frame(self.right_upper_frame)
        self.main_right_frame.pack(side="right")
        self.spectators_label = tk.Label(self.main_right_frame, text="Spectators:")
        self.spectators_label.pack()
        self.spectators_listbox = tk.Listbox(self.main_right_frame)
        self.spectators_listbox.pack()

        self.right_bottom_frame = tk.Frame(self.right_frame)
        self.right_bottom_frame.pack(side="bottom")

        self.board_frame = tk.Frame(self.right_bottom_frame)
        self.board_frame.pack(side="bottom")
        self.board_label = tk.Label(self.board_frame, text="Board:")
        self.board_label.pack()
        self.board_text = tk.Text(self.board_frame, width=20, height=10)
        self.board_text.pack()
        self.board_text.config(state="disabled")

        self.root.mainloop()

    def send_to_all_clients(self, message):
        for client, _ in self.clients.values():
            client.send(message.encode())

    def send_to_all_clients_except(self, message, username):
        for client, _ in self.clients.values():
            if client != self.clients[username][0]:
                client.send(message.encode())

    def log(self, message):
        self.log_text_box.insert(tk.END, f"{message}\n")

    def update_server_board(self):
        self.board_text.config(state="normal")
        self.board_text.delete("1.0", tk.END)
        self.board_text.insert(tk.END, self.game.board_repr())
        self.board_text.config(state="disabled")

    def start_game(self):
        if len(self.players) == 2:
            symbols = ['X', 'O']
            random.shuffle(symbols)
            players = {}
            spectators = {}

            self.games_text.config(state="normal")
            self.games_text.delete(1.0, tk.END)
            self.games_text.insert(tk.END, str(self.games_played))
            self.games_text.config(state="disabled")

            for i, username in enumerate(self.players):
                client_socket, _ = self.clients[username]
                symbol = symbols[i]
                client_socket.send(f"SYMBOL {symbol}\n".encode())
                self.log(f"{username} is appointed {symbol}")
                players[username] = (client_socket, symbol)

            if len(self.spectators) != 0:
                for username in self.spectators:
                    client_socket, client_address = self.clients[username]
                    spectators[username] = (client_socket,)

            self.log(f"Game {self.games_played} started\n")
            self.game = TicTacToeGame(players, spectators)

            self.update_server_board()
            self.game.broadcast_board()

            time.sleep(0.1)

            first_player = None
            second_player = None
            for player, (client_socket, symbol) in self.game.players.items():
                if symbol == 'X':
                    first_player = player
                    break

            for player, (client_socket, symbol) in self.game.players.items():
                if symbol == 'O':
                    second_player = player
                    break

            first_player_socket = self.clients[first_player][0]
            first_player_socket.send(f"YOUR_TURN".encode())
            self.log(f"It's {first_player}'s turn")

            second_player_socket = self.clients[second_player][0]
            second_player_socket.send(f"OPPONENT_TURN {first_player}".encode())

            for spectator in self.spectators:
                spectator_socket = self.clients[spectator][0]
                spectator_socket.send(f"MESSAGE It's {first_player}'s turn\n".encode())
        else:
            return

    def start_server(self):
        port = int(self.port_entry.get())
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.bind((socket.gethostname(), port))
            self.sock.listen()
            self.log_text_box.insert(tk.END, f"Server started on port {port}\n")
            self.status_label.config(text="Server is running", fg="green")
            self.start_button.config(state="disabled")
            self.port_entry.config(state="disabled")
            self.stop_button.config(state="normal")
            threading.Thread(target=self.receive).start()
        except Exception as e:
            self.log_text_box.insert(tk.END, f"Failed to start server: {str(e)}\n")

    def receive(self):
        while True:
            try:
                client_socket, client_address = self.sock.accept()
                username = client_socket.recv(1024).decode()

                if len(self.clients) >= 4:
                    client_socket.send("MESSAGE Server is full".encode())
                    sleep(0.1)
                    client_socket.close()
                    continue

                if username in self.clients:
                    client_socket.send("MESSAGE Username already taken".encode())
                    client_socket.close()
                    continue

                self.clients[username] = (client_socket, client_address)
                client_socket.send("MESSAGE Connected to the server".encode())
                self.log(f"{username} connected.")

                # If game is None and less than 2 players
                if self.game is None and len(self.players) < 2:
                    self.players.append(username)
                    self.players_listbox.insert(tk.END, username)
                    client_socket.send("MESSAGE You are a player\n".encode())
                    if len(self.players) == 2:
                        self.start_game()

                # If game is not None and less than 2 players
                elif self.game is not None and len(self.players) < 2:
                    self.players.append(username)
                    self.players_listbox.insert(tk.END, username)
                    client_socket.send("MESSAGE You are a player\n".encode())

                # If game is not None and already 2 players
                else:
                    self.spectators.append(username)
                    self.game.spectators[username] = (client_socket,)  # add the client to game spectators
                    self.spectators_listbox.insert(tk.END, username)
                    client_socket.send("MESSAGE You are a spectator\n".encode())
                    if self.game is not None:
                        self.game.add_spectator(username, client_socket)

                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address, username))
                client_thread.start()

            except socket.error:
                self.log_text_box.insert(tk.END, "Error: Connection lost\n")
                break

    def handle_client(self, client_socket, client_address, username):
        while True:
            try:
                message = client_socket.recv(1024).decode()
                if message:
                    if message.startswith("MOVE"):
                        _, cell = message.split()
                        cell = int(cell)
                        if username in self.players and self.game:
                            symbol = self.game.players[username][1]
                            valid_move, game_status = self.game.make_move(cell, symbol)
                            if valid_move:
                                time.sleep(0.1)
                                client_socket.send("VALID_MOVE".encode())
                                
                                self.log(f"VALID_MOVE message sent to {username}.")
                                self.log(f"{username} made a move at cell {cell}.")
                                self.log(f"Game status: {game_status}\n")
                                self.update_server_board()

                                if game_status[0] == "end":
                                    if game_status[1] == "win":
                                        winning_symbol = game_status[2]
                                        winning_player = None
                                        for player, (client_socket, symbol) in self.game.players.items():
                                            if symbol == winning_symbol:
                                                winning_player = player
                                                break
                                        winning_player_socket = self.clients[winning_player][0]
                                        winning_player_socket.send(f"Win".encode())
                                        time.sleep(0.1)
                                        self.log(f"WIN message has been sent to {winning_player}\n")
                                        losing_player = self.game.get_opponent_username(winning_player)
                                        losing_player_socket = self.clients[losing_player][0]
                                        losing_player_socket.send(f"LOSS".encode())
                                        time.sleep(0.1)
                                        self.log(f"LOSS message has been sent to {losing_player}\n")
                                        self.log(f"{winning_player} won!\n")

                                        for spectator in self.spectators:
                                            spectator_socket = self.clients[spectator][0]
                                            spectator_socket.send(f"MESSAGE {winning_player} won!\n".encode())

                                    elif game_status[1] == "draw":
                                        self.send_to_all_clients(f"DRAW")
                                        time.sleep(0.1)
                                        self.log("It's a draw.\n")

                                    self.games_played += 1
                                    self.games_text.config(state="normal")
                                    self.games_text.delete(1.0, tk.END)
                                    self.games_text.insert(tk.END, str(self.games_played))
                                    self.games_text.config(state="disabled")

                                    self.start_game()

                                elif game_status[0] == "continue":
                                    turn_username = ""
                                    not_turn_username = ""

                                    current_turn = self.game.turn
                                    if current_turn == symbol:
                                        self.log(f"It's {username}'s turn.\n")
                                        opponent_username = self.game.get_opponent_username(username)
                                        not_turn_username = opponent_username
                                        turn_username = username
                                    else:
                                        opponent_username = self.game.get_opponent_username(username)
                                        self.log(f"It's {opponent_username}'s turn.\n")
                                        turn_username = opponent_username
                                        not_turn_username = username

                                    turn_player_socket, _ = self.game.players[turn_username]
                                    not_turn_player_socket, _ = self.game.players[not_turn_username]
                                    time.sleep(0.1)
                                    turn_player_socket.send(f"YOUR_TURN".encode())
                                    time.sleep(0.1)
                                    not_turn_player_socket.send(f"OPPONENT_TURN {turn_username}".encode())

                                    time.sleep(0.1)

                                    for spectator in self.spectators:
                                        spectator_socket = self.clients[spectator][0]
                                        spectator_socket.send(f"MESSAGE It's {turn_username}'s turn.".encode())

                                continue
                            else:
                                client_socket.send("INVALID_MOVE".encode())
                        else:
                            client_socket.send("INVALID_MOVE".encode())
                    else:
                        if message == "Disconnect":
                            self.log(f"{username} disconnected")
                            self.clients.pop(username)

                            if username in self.players:
                                index = self.players.index(username)
                                disconnected_player_symbol = self.game.players[username][1]
                                self.game.players.pop(username)
                                self.players.pop(index)
                                self.players_listbox.delete(index)
                                self.send_to_all_clients(f"MESSAGE Player {username} has disconnected and/or left the game.")
                                self.log(f"Player {username} has disconnected and/or left the game.")

                                if self.spectators:
                                    # Replace the disconnected player with a spectator
                                    new_player = self.spectators.pop(0)
                                    self.game.spectators.pop(new_player)  # remove the client from game spectators
                                    self.players.append(new_player)
                                    self.players_listbox.insert(tk.END, new_player)
                                    self.spectators_listbox.delete(0)

                                    # Rearrange spectator indices to reflect changes
                                    self.spectators = [self.spectators[i] for i in range(len(self.spectators))]

                                    if len(self.players) == 2:
                                        other_player = self.players[0] if self.players[1] == new_player else self.players[1]
                                        self.send_to_all_clients(f"MESSAGE Opponent {username} is now replaced by {new_player}")
                                        self.log(f"Opponent {username} is now replaced by {new_player}")

                                        new_player_socket = self.clients[new_player][0]
                                        self.game.players[new_player] = (new_player_socket, disconnected_player_symbol)  # add the client to game players
                                        new_player_socket.send(f"SYMBOL {disconnected_player_symbol}\n".encode())
                                        new_player_socket.send(f"MESSAGE You are joining the game as an opponent!\n".encode())
                                        self.log(f"{new_player} is joining the game as an opponent!")

                                        if self.game.turn == disconnected_player_symbol:
                                            self.game.turn = self.game.players[new_player][1]

                                        new_player_socket = self.clients[new_player][0]
                                        other_player_socket = self.clients[other_player][0]
                                        time.sleep(0.1)
                                        if self.game.turn == self.game.players[new_player][1]:
                                            new_player_socket.send(f"YOUR_TURN".encode())
                                            other_player_socket.send(f"OPPONENT_TURN {new_player}".encode())
                                        else:
                                            new_player_socket.send(f"OPPONENT_TURN {other_player}".encode())
                                            other_player_socket.send(f"YOUR_TURN".encode())
                                else:
                                    self.send_to_all_clients(f"MESSAGE There are no available replacements. The game is over.")
                                    self.log(f"There are no available replacements. The game is over.")

                                    # Reset the game
                                    self.game = None

                                client_socket.close()
                                break
                            else:
                                self.log(f"{username}: {message}")
                                self.send_to_all_clients(f"{username}: {message}")

            except socket.error:
                self.clients.pop(username)
                client_socket.close()
                break

    def stop_server(self):
        message = "MESSAGE Server has disconnected."
        for client_socket, _ in self.clients.values():
            try:
                client_socket.send(message.encode())
                client_socket.close()
            except Exception as e:
                self.log_text_box.insert(tk.END, f"Failed to disconnect client: {str(e)}\n")
        self.clients.clear()
        self.players_listbox.delete(0, tk.END)
        self.spectators_listbox.delete(0, tk.END)
        self.players.clear()
        self.spectators.clear()
        self.games_played = 0
        try:
            if self.sock:
                try:
                    self.sock.send(b'')
                except Exception as e:
                    pass
                else:
                    self.sock.shutdown(socket.SHUT_RDWR)
                self.sock.close()
        except Exception as e:
            self.log_text_box.insert(tk.END, f"Failed to stop server: {str(e)}\n")
        self.log_text_box.insert(tk.END, f"Server stopped\n")
        self.status_label.config(text="Server is not running", fg="red")
        self.start_button.config(state="normal")
        self.port_entry.config(state="normal")
        self.stop_button.config(state="disabled")


if __name__ == "__main__":
    host = socket.gethostbyname(socket.gethostname())
    server = Server(host)