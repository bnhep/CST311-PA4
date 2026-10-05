#!env python
"""
Brandon Nhep
CST 311, Introduction to Computer Networks
Programming Assignment 4
10/25/2025
"""
"""Chat client for CST311 Programming Assignment 3"""
__author__ = "[Brandon Nhep]"

# Import statements
import socket as s
import threading
# Configure logging
import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# Set global variables
server_name = '10.0.20.2'
server_port = 12000

# Function to handle receiving responses from server
def receive_server_response(client_socket):
  # Loop to keep checking for server responses
  while True:
    try:
      # Read response from server
      server_response = client_socket.recv(1024)
      # Decode server response from UTF-8 bytestream
      server_response_decoded = server_response.decode()
      if server_response:
        # Check for quit message to exit loop and thread
        if server_response_decoded.strip().lower() == "quit":
          break
        # Print the output from the server
        print(server_response_decoded)
      else:
        break
    # Catch exceptions and log and break loop
    except Exception as e:
      log.exception("Error receiving server response: " + str(e))
      break

# Function to handle sending input from user/client to server
def send_input(client_socket):
  # Loop to keep checking for user input
  while True:
    try:
      # Get input from user
      user_input = input('')
      # Send user input to server
      user_input_encoded = user_input.encode()
      # Send encoded user input to server
      client_socket.send(user_input_encoded)
      # Check for bye message to exit this loop and thread
      if user_input.strip().lower() == "bye":
        break
    # Catch exceptions and log and break loop
    except Exception as e:
      log.exception("Error sending user input: " + str(e))
      break

def main():
  # Create socket
  client_socket = s.socket(s.AF_INET, s.SOCK_STREAM)
  try:
    # Establish TCP connection
    client_socket.connect((server_name,server_port))
  except Exception as e:
    log.exception(e)
    log.error("***Advice:***")
    if isinstance(e, s.gaierror):
      log.error("\tCheck that server_name and server_port are set correctly.")
    elif isinstance(e, ConnectionRefusedError):
      log.error("\tCheck that server is running and the address is correct")
    else:
      log.error("\tNo specific advice, please contact teaching staff and include text of error and code.")
    exit(8)

  # Wrap in a try-finally to ensure the socket is properly closed regardless of errors
  try:
    # create threads for sending and receiving messages
    # thread1 for receiving messages
    # thread2 for sending messages
    thread1 = threading.Thread(target=receive_server_response, args=(client_socket,))
    thread2 = threading.Thread(target=send_input, args=(client_socket,))
    # start threads to run concurrently
    thread1.start()
    thread2.start()
    # wait for threads to finish before exiting
    thread1.join()
    thread2.join()

  finally:
    # Close socket prior to exit
    client_socket.close()

# This helps shield code from running when we import the module
if __name__ == "__main__":
  main()
  
# Referenced document for tcp sockets
# To understand the basics of TCP sockets
# https://realpython.com/python-sockets/

# Referenced
# To understand the basics of threading, starting threads, and joining threads
# used in main function when creating the threads
# https://realpython.com/intro-to-python-threading/
# https://www.youtube.com/watch?v=6eqC1WTlIqc

# Referenced
# to understand how responses and inputs can be handled concurrently
# used in receive_server_response and send_input functions
# https://labex.io/tutorials/python-how-to-send-and-receive-messages-using-python-sockets-398244#building-a-client-to-connect-to-the-server