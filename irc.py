# IRC chat program

import socket
import select
import string
import sys
import threading
import time

# Function for sending data to specific clients
def send_data(sock, message, client_list, server_socket):
    for socket in client_list:
        if socket != server_socket and socket != sock:
            try:
                socket.send(message)
            except:
                # Client disconnected
                socket.close()
                client_list.remove(socket)

# Writes the port number to file for list of running server ports
def save_port(port):
    file = open("port_list.txt", "a+")
    file.write(str(port)+"\n")
    file.close()

# Removes the port number before server shuts down
def remove_port(port):
    file = open("port_list.txt", "r")
    lines = file.readlines()
    file.close()

    file = open("port_list.txt", "w")
    for line in lines:
        if line != str(port) + "\n":
            file.write(line)
    file.close()

# Ooo SO FANCY!
def flair():
    sys.stdout.write("(This Is You) ")
    sys.stdout.flush()

def print_ports():
    file = open("port_list.txt", "r")
    line = file.readline()
    while line:
        print line
        line = file.readline()
    file.close()

def run_server(port):

    # Variable to keep track of the clients,
    # buffer for incoming data, and port number
    client_list = []
    read_buff = 2048

    # Initialize socket connections to Ipv4(AF_INET) and TCP(SOCK_STREAM)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Set to reusable so we dont get "in use" errors when launching server
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind to the port and begin listening
    server_socket.bind(("0.0.0.0", port))
    server_socket.listen(10)
    client_list.append(server_socket)

    print "Server started on port " + str(port)
    print "Type: 'server exit' while in client to terminate server"
    save_port(port)

    control = 1
    while control:
        # Get sockets that are ready to be used
        read_sockets,write_sockets,error_sockets = select.select(client_list,[],[])

        for sock in read_sockets:
            # Add new connections if present
            if sock == server_socket:
                sockfd, addr = server_socket.accept()
                client_list.append(sockfd)
                print "Client (%s, %s) has connected" % addr

            else:
                # Incoming message
                data = sock.recv(read_buff)
                stringdata = data.decode('utf-8')
                if stringdata == "server exit\n":
                    control = 0
                else:
                    if data:
                        send_data(
                        sock, "\r" + str(sock.getpeername()) + " " + data,
                        client_list, server_socket)
                    else:
                        send_data(
                        sock, "\nClient (%s, %s) disconnected from chat\n" % addr,
                        client_list, server_socket)
                        print "Client (%s, %s) has disconnected" % addr
                        sock.close()
                        client_list.remove(sock)
                        continue

    print "Shutting Down Server"
    remove_port(port)
    server_socket.close()

def run_client(host, port):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)

    # Connect to the host server
    try:
        s.connect((host, port))
    except:
        print "Could not connect to server"
        sys.exit()

    print "Connected to the server!"
    print "Type: 'client exit' to return to UI"
    flair()

    control0 = 1
    while control0:
        socket_list = [sys.stdin, s]

        # Select the list of sockets that can be connected to
        read_sockets,write_sockets,error_sockets = select.select(socket_list,[],[])

        for sock in read_sockets:
            # Server is sending something
            if sock == s:
                data = sock.recv(2048)
                if not data:
                    print "\nDisconnected from chat room\n"
                    sys.exit()
                else:
                    # Print the message from server
                    sys.stdout.write(data)
                    flair()

            # User typed a thing. Send it.
            else:
                msg = sys.stdin.readline()
                stringmsg = msg.decode('utf-8')
                if stringmsg == "client exit\n":
                    control0 = 0
                else:
                    s.send(msg)
                    flair()

if __name__ == "__main__":

    # Change host to run on different machine
    host = "crimson-VirtualBox"
    threads = []

    while 1:
        print "\nWhat would you like to do?\n"
        print "1) Host & Join a Room\n2) Join a Chat Room"
        print "3) List Available Rooms\n4) Exit\n"
        print "ATTENTION! Not every port value will work for a room."
        print "Chat servers can only be shutdown with client commands"
        response = input()
        if response == 1:
            port = input("Please enter a port number to use\n")
            t1 = threading.Thread(target=run_server, args=(port,))
            threads.append(t1)
            t1.setDaemon(True)
            t1.start()
            time.sleep(1)
            run_client(host,port)
        if response == 2:
            port = input("Please enter a port to connect to\n")
            run_client(host,port)
        if response == 3:
            print "Chat Room Port Numbers:\n"
            print_ports()
        if response == 4:
            break
    print "Exiting UI..."
