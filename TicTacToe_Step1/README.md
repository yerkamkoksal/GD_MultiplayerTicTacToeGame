# Multiplayer TicTacToe Game

## Description
Developed by Yusuf Erkam Köksal for CS408 Term Project, this Multiplayer TicTacToe game allows two players to play TicTacToe over a network. The game is implemented in Python using the `tkinter` library for the GUI and `socket` programming for the network communication. 

## Features
- Interactive GUI for both the server and client.
- Network communication between the server and multiple clients.
- Real-time game updates and move validation.
- Display of game status (win, loss, draw, turn) to players.
- Connection management for handling multiple players.

## Usage
1. **Run the Server Program**: Start the server to listen for incoming client connections.
2. **Connect Clients**: Players can connect to the server by entering the server's IP address and port number.
3. **Play TicTacToe**: Players take turns to make their moves. The game updates in real-time and displays on both clients' GUIs.

### Example Usage
- Server:
    - Start the server application.
    - Enter the port number and click "Start Server".
- Client:
    - Start the client application.
    - Enter the server's IP address, port number, and a username.
    - Click "Connect" to join the game.
    - Make moves by entering cell numbers.

## Installation
To run the game, ensure Python is installed on your system. The game uses the standard Python libraries `tkinter` and `socket`, so no additional installations are required.

## Note
- The game is designed for two players.
- Players should take turns in a coordinated manner as per the game's instructions.
- The server must be running and reachable for clients to connect and play.

## Contributors
- Yusuf Erkam Köksal
