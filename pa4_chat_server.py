#!env python
"""
Brandon Nhep
CST 311, Introduction to Computer Networks
Programming Assignment 4
10/25/2025
"""
"""Chat server for CST311 Programming Assignment 3"""
__author__ = "[Brandon Nhep]"

import socket as s
import threading
import time

# Configure logging
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

server_port = 12000

# Global variables
# List of clients namedtuple (connection socket, address, name)
clients_list = []
# Lock to manage the concurrency of client connections
# allows only one thread to modify the clients list, counter, and
# boolean of client_disconnections at a time
client_lock = threading.Lock()
# Counter to assign client names based on order of connection
client_counter = 0
# Boolean to indicate if all clients have disconnected
all_clients_disconnected = False

"""Function to assign usernames to clients based on order of connection"""
def assign_username(connection_socket, address):
  global client_counter, clients_list, all_clients_disconnected, client_lock
  # increment client counter to track number of clients
  client_counter += 1
  # Assign names Client X and Client Y to first two clients
  # unpack the existing client tuples to get their names in order to check
  # for duplicates
  previous_names = []
  # Get names from previous/existing clients
  for connection, addr, name in list(clients_list):
    previous_names.append(name)
  # Check existing names to avoid duplicates
  if "Client X" not in previous_names:
    client_name = "Client X"
  elif "Client Y" not in previous_names:
    client_name = "Client Y"
  elif "Client Z" not in previous_names:
    client_name = "Client Z"
  else:
    client_name = "Client " + str(client_counter)
  # Add the new client name to the list of clients,
  # with connection socket, address, and assigned name as a tuple
  # output the connection info to the console
  clients_list.append((connection_socket, address, client_name))
  print("Connected to " + client_name + " at " + str(address))

"""Function to handle client quitting the chat"""
def handle_quit(connection_socket):
  global client_counter, clients_list, all_clients_disconnected, client_lock
  # Find the name of the client that is quitting
  client_name = None
  client_name = get_client_name(connection_socket)
  # Send QUIT message to client to signal them to close their socket and thread
  try:
    connection_socket.send("QUIT".encode())
  except Exception as e:
    log.exception("Error sending QUIT message: " + str(e))
  # Remove the client from the clients list if they say bye
  # unpack the tuples to find the matching connection socket
  for connection, addr, name in list(clients_list):
    if connection == connection_socket:
      clients_list.remove((connection, addr, name))
      client_counter -= 1
  # Notify the other clients that this client has left the chat
  # unpack the tuples to get the connection sockets of other clients
  if client_name:
    exit_message = client_name + " has left the chat."
    for connection, addr, name in list(clients_list):
      if connection != connection_socket:
        try:
          connection.send(exit_message.encode())
        except Exception as e:
          log.exception("Error sending EXIT message: " + str(e))

"""Function to get the name of a client based on their connection socket"""
# needs to be called within a lock to ensure safe access to clients_list
def get_client_name(connection_socket):
  global clients_list
  # Check the clients list for the matching connection socket
  # return the name if found, else return None
  for connection, addr, name in list(clients_list):
    if connection == connection_socket:
      return name
  return None

"""Function to handle each client connection in a separate thread"""
def connection_handler(connection_socket, address):
  # Use the global client_counter, clients_list, disconnect checker
  global client_counter, clients_list, all_clients_disconnected, client_lock
  # Send welcome message to the client after connection is established
  client_username = None
  welcome_message = "Welcome to the chat! To send a message, type the message and click enter."
  connection_socket.send(welcome_message.encode())
  # Use a lock to ensure safe access to the shared data clients, counter,
  # and disconnect checker boolean
  # Call assign_username to assign a username to the new client
  with client_lock:
    assign_username(connection_socket, address)
    # call get_client_name to retrieve the assigned username
    client_username = get_client_name(connection_socket)
  # Read and send data with the new connection socket
  try:
    # Loop to listen for messages from client
    while True:
      try:
        # Receive up to 1024 bytes from client
        query = connection_socket.recv(1024)
        # If no data, client has disconnected
        if not query:
          break
        # Decode bytes to string
        query_decoded = query.decode()
        # If client says bye, remove them from clients list and notify other client
        # send QUIT to client to signal them to close their socket
        if query_decoded.strip().lower() == "bye":
          # Use lock to ensure safe modification of shared data across threads
          with client_lock:
            handle_quit(connection_socket)
          # Exit the loop and end the thread
          break

        # Broadcast the received message to the other client if not bye
        # Use lock to ensure safe access to shared data
        with client_lock:
          # Won't start forwarding until at least 2 clients are connected
          # restart loop to check for new connections
          if len(clients_list) < 2:
            connection_socket.send(
              "Waiting for another client to connect...".encode())
            continue
          # If two clients are connected, forward the message
          else:
            # Format the message with the client's name
            response = client_username + ": " + query_decoded
            # Send the message to the other clients
            # unpack the tuples to get connection sockets of other clients
            for connection, addr, name in list(clients_list):
              if connection != connection_socket:
                try:
                  connection.send(response.encode())
                except Exception as e:
                  log.exception("Error sending message to client: " + str(e))
                  # If sending fails, client may have disconnected
                  # handle removal/disconnect of that client
                  connection.close()
                  clients_list.remove((connection, addr, name))
                  client_counter -= 1
      except Exception as e:
        log.exception("Error in communication with client: " + str(e))
        break
  # Makes sure the client socket is closed and removed from clients list
  finally:
    # Close client socket
    connection_socket.close()
    # Remove client from clients list when disconnected/finished
    with client_lock:
      # unpack the tuples to find the matching connection socket
      for connection, addr, name in list(clients_list):
        if connection == connection_socket:
          clients_list.remove((connection, addr, name))
          client_counter -= 1
      print(client_username + " at " + str(address) + " has disconnected.")
      # If no clients are left, set the disconnect checker boolean to True
      # so that main loop can exit if needed and quit program
      if not clients_list:
        client_counter = 0
        all_clients_disconnected = True

"""Main function to set up the server and listen for connections"""
def main():
  # Create a TCP socket
  # Notice the use of SOCK_STREAM for TCP packets
  server_socket = s.socket(s.AF_INET,s.SOCK_STREAM)
  
  # Assign port number to socket, and bind to chosen port
  server_socket.bind(('',server_port))
  
  # Configure how many requests can be queued on the server at once
  server_socket.listen(7)
  
  # Alert user we are now online
  print("Server listening on port " + str(server_port))

  # Surround with a try-finally to ensure we clean up the socket after we're done
  try:
    # Enter forever loop to listen for requests
    while True:
      # use timeout to periodically check if main loop should exit
      server_socket.settimeout(1.0)
      try:
        # When a client connects, create a new socket and record their address
        connection_socket, address = server_socket.accept()
        # Pass the new socket and address off to a connection handler function
        # that runs in a new thread
        thread1 = threading.Thread(target=connection_handler, args=(connection_socket, address))
        thread1.start()
      # Timeout every second to check if main loop should exit
      except s.timeout:
        pass
      # If all clients have disconnected, break the loop and exit
      with client_lock:
        if all_clients_disconnected:
          break
  # Close socket prior to exit
  finally:
    server_socket.close()

if __name__ == "__main__":
  main()


# Referenced documents for settimeout
# in order for main to check if clients are disconnected and exit if they are
# https://docs.python.org/3/library/time.html
# https://docs.python.org/3/library/socket.html

# Referenced
# To understand Thread locking and providing insight on how to use locks for
# connection_handler using threading.Lock() and with client_lock:
# https://realpython.com/python-thread-lock/

# Referenced to understand the basics of TCP sockets such as socket creation, binding,
# listening, accepting connections, sending and receiving data
# https://realpython.com/python-sockets/

# Referenced for error handling in socket communication try-except blocks
# and try-finally blocks
# https://labex.io/tutorials/python-how-to-implement-error-handling-in-python-socket-communication-398023