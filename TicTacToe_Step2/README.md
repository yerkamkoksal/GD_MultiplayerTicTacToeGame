# Enhanced Multiplayer TicTacToe Game

## Description
An extension of Yusuf Erkam Köksal's Multiplayer TicTacToe game, this version introduces enhanced multiplayer attributes, including the ability for players to join or leave during the game, and automatic management of games starting and ending.

## Features
- Players can connect and disconnect from the game server dynamically.
- The game supports spectators, who can view the game in progress.
- Automatic handling of player disconnections, with replacements from spectators if available.
- Real-time update of the game board and player/spectator lists.
- Enhanced server control with GUI for starting, stopping, and monitoring the server and games.

## Usage
### Server:
- Start the server by entering the port number and clicking "Start".
- Monitor connected players and spectators in real-time.
- View logs and status of ongoing games.

### Client:
- Connect to the server using the provided IP address and port number.
- Play TicTacToe in real-time with other connected players.
- Disconnect and reconnect to the game as needed.

### Example Workflow:
1. **Server Setup**: Launch the server application, enter the desired port, and start the server.
2. **Player Connection**: Players connect to the server by entering its IP address and port number.
3. **Gameplay**: Players take turns to play TicTacToe, with their moves updated in real-time.
4. **Spectators**: Additional clients can join as spectators to watch the ongoing game.
5. **Player Disconnection/Reconnection**: Players can leave and rejoin, with the server handling game continuity.

## Installation
Python is required to run the game. The game uses standard Python libraries `tkinter` for the GUI and `socket` for network communication.

## Note
- The server must be active for clients to connect and play.
- Ensure network configurations allow client-server communication.
- The game is designed for two active players with additional spectators.

## Contributors
- Yusuf Erkam Köksal
