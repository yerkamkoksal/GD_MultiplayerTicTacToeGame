import tkinter as tk
import socket
import threading
 
class Client: #Client class to handle the GUI and the connection to the server
    def __init__(self): #Constructor
        
        self.root = tk.Tk()
        self.root.title("Client")
        self.root.geometry("400x400")

        self.symbol = "" #Symbol of the player
        self.board = [] #Board of the game
        self.opponent_username = "" #Username of the opponent

        self.logs_frame = tk.Frame(self.root)
        self.logs_frame.pack(side="left")
        self.status_label = tk.Label(self.root, text="Not connected", fg="red")
        self.status_label.pack()

        self.ip_label = tk.Label(self.root, text="IP:")
        self.ip_label.pack()
        self.ip_entry = tk.Entry(self.root) #Entry widget to get the IP address
        self.ip_entry.pack()
        self.port_label = tk.Label(self.root, text="Port:")
        self.port_label.pack()
        self.port_entry = tk.Entry(self.root) #Entry widget to get the port number
        self.port_entry.pack()
        self.username_label = tk.Label(self.root, text="Username:")
        self.username_label.pack()
        self.username_entry = tk.Entry(self.root) #Entry widget to get the username
        self.username_entry.pack()
        self.connect_button = tk.Button(self.root, text="Connect", command=self.connect_and_check)
        self.connect_button.pack()
        self.disconnect_button = tk.Button(self.root, text="Disconnect", command=self.disconnect)
        self.disconnect_button.pack()

        self.move_label = tk.Label(self.root, text="Move:")
        self.move_label.pack()
        self.move_entry = tk.Entry(self.root) #Entry widget to get the move
        self.move_entry.pack()
        self.move_button = tk.Button(self.root, text="MOVE", command=self.send_move, state="disabled")
        self.move_button.pack()

        self.board_frame = tk.Frame(self.root)
        self.board_frame.pack(side="right")
        self.board_label = tk.Label(self.board_frame, text="Board:") 
        self.board_label.pack()
        self.board_text = tk.Text(self.board_frame, width=20, height=10) #Text widget to display the board
        self.board_text.pack()
        self.board_text.config(state="disabled")

        self.logs = tk.Text(self.logs_frame, width=20, height=20) #Text widget to display the logs
        self.logs.pack()
        self.logs.config(state="disabled")

        self.root.mainloop()

    def connect_and_check(self): #Function to connect to the server and check if the connection is successful
        self.connect_button.config(state="disabled") 
        self.logs.config(state="normal")
        self.logs.insert(tk.END, "Connecting...\n")
        self.logs.config(state="disabled")

        self.host = self.ip_entry.get() #Get the IP address
        self.port = int(self.port_entry.get()) #Get the port number
        self.username = self.username_entry.get() #Get the username

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Create a socket
        try:
            self.client_socket.connect((self.host, self.port)) #Connect to the server
        except:
            self.logs.config(state="normal")
            self.logs.insert(tk.END, "Could not connect to the server\n") #If the connection is unsuccessful display an error message
            self.logs.config(state="disabled")
            self.connect_button.config(state="normal")
            return

        self.client_socket.send(self.username.encode()) #Send the username to the server
        response = self.client_socket.recv(1024).decode() #Receive a response from the server
        if response != "Connected to the server": #If the response is not "Connected to the server" display an error message
            self.logs.config(state="normal")
            self.logs.insert(tk.END, "Could not connect to the server\n" + response) #Display the error message
            self.logs.config(state="disabled")
            self.client_socket.close()
            self.connect_button.config(state="normal")
            return

        self.logs.config(state="normal")
        self.logs.insert(tk.END, "Connected to the server\n") #If the connection is successful display a success message
        self.logs.config(state="disabled")
        self.status_label.config(text="Connected", fg="green")
        self.ip_entry.config(state="disabled")
        self.port_entry.config(state="disabled")
        self.username_entry.config(state="disabled")
        self.connect_button.config(state="disabled")
        self.disconnect_button.config(state="normal")
        self.connected = True

        response_thread = threading.Thread(target=self.receive) #Create a thread to receive messages from the server
        response_thread.start() 

    def display_board(self, board_repr): #Function to display the board
        self.board_text.config(state="normal")
        self.board_text.delete('1.0', tk.END)
        self.board_text.insert(tk.END, "Board:\n\n")
        self.board_text.insert(tk.END, board_repr)
        self.board_text.config(state="disabled")

    def disconnect(self): #Function to disconnect from the server
        self.client_socket.send("Disconnect".encode())
        self.client_socket.close()
        self.root.destroy()

    def send_move(self): #Function to send the move to the server
        move = self.move_entry.get() #Get the move
        if not move:
            return
        cell = int(move)
        if 1 <= cell <= 9: #Check if the move is valid
            self.client_socket.send(f"MOVE {cell}".encode()) #Send the move to the server


    def receive(self): #Function to receive messages from the server
        while True: #Loop to receive messages from the server
            try:
                message = self.client_socket.recv(1024).decode() 
                if message == "Disconnect": #If the message is "Disconnect" close the connection
                    self.client_socket.close()
                    break

                self.handle_server_message(message) #Handle the message
            except:
                self.logs.config(state="normal")
                self.logs.insert(tk.END, "Error: Connection lost\n")
                self.logs.config(state="disabled")
                self.status_label.config(text="Disconnected", fg="red")
                self.ip_entry.config(state="normal")
                self.port_entry.config(state="normal")
                self.username_entry.config(state="normal")
                self.connect_button.config(state="normal")
                self.disconnect_button.config(state="disabled")
                self.move_button.config(state="disabled")
                break


    def handle_server_message(self, message): #Function to handle the messages from the server
        tokens = message.split()

        if tokens[0] == f"SYMBOL": #If the message is "SYMBOL" get the symbol of the player
            self.symbol = tokens[1]
            self.logs.config(state="normal")
            self.logs.insert(tk.END, f"Your symbol is: {self.symbol}\n") #Display the symbol of the player
            self.logs.config(state="disabled")

        elif tokens[0] == f"BOARD": #If the message is "BOARD" display the board
            board_data = "".join(tokens[1:])
            board_repr = board_data[:5] + "\n" + \
                        board_data[5:10] + "\n" + \
                        board_data[10:]
            self.display_board(board_repr) #Display the board

        elif tokens[0] == f"MESSAGE": #If the message is "MESSAGE" display the message
            self.logs.config(state="normal")
            self.logs.insert(tk.END, ' '.join(tokens[1:]) + "\n") #Display the message
            self.logs.config(state="disabled")

        elif tokens[0] == f"VALID_MOVE": #If the message is "VALID_MOVE" display a success message
            self.logs.config(state="normal")
            self.logs.insert(tk.END, f"Valid move\n") #Display a success message
            self.logs.config(state="disabled")
            self.move_entry.delete(0, 'end')

        elif tokens[0] == f"INVALID_MOVE": #If the message is "INVALID_MOVE" display an error message
            self.logs.config(state="normal")
            self.logs.insert(tk.END, f"Invalid move!\nTry again\n") #Display an error message
            self.logs.config(state="disabled")
            self.move_entry.delete(0, 'end') #Clear the move entry

        elif tokens[0] == f"YOUR_TURN": #If the message is "YOUR_TURN" enable the move button 
            self.logs.config(state="normal")
            self.logs.insert(tk.END, f"It's your turn\n") #Display a success message
            self.logs.config(state="disabled")
            self.move_entry.delete(0, 'end') #Clear the move entry
            self.move_button.config(state="normal")

        elif tokens[0] == f"OPPONENT_TURN": #If the message is "OPPONENT_TURN" display a message  
            self.logs.config(state="normal")
            self.logs.insert(tk.END, f"It's opponent's turn\n") #Display a message
            self.logs.config(state="disabled")
            self.move_entry.delete(0, 'end') #Clear the move entry
            self.move_button.config(state="disabled")

        elif tokens[0] == f"WIN": #If the message is "WIN" display a message
            self.logs.config(state="normal")
            self.logs.insert(tk.END, f"You won!\n") #Display a message
            self.logs.config(state="disabled")
            self.move_button.config(state="disabled")

        elif tokens[0] == f"LOSS": #If the message is "LOSS" display a message
            self.logs.config(state="normal")
            self.logs.insert(tk.END, f"You lost!\n") #Display a message
            self.logs.config(state="disabled")
            self.move_button.config(state="disabled")

        elif tokens[0] == f"DRAW": #If the message is "DRAW" display a message
            self.logs.config(state="normal")
            self.logs.insert(tk.END, f"It's a draw!\n") #Display a message
            self.logs.config(state="disabled")
            self.move_button.config(state="disabled")





if __name__ == "__main__":
    client = Client()