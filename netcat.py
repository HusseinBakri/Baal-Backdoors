'''
Source: https://code.sololearn.com/cuvVQ9ZJvR5q/#py

I tweaked it and transformed it to Python 3
'''

#!/usr/bin/python
import sys
import socket
import getopt
import threading
import subprocess

# Define global variables
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0


def usage():
    print("Python Netcat replacement tool!!\n")
    print("Usage: netcat.py -t target_host -p port")
    print("-l --listen      -listen on [host]:[port] for incoming connections")
    print("-e --execute=file_to_run  -execute the given file upon receiving a connection.")
    print("-c --command     -initialize a command shell.")
    print(
        "-u --upload=destination  -upon receiving connection uploada file and write [destination].\n")
    print("Examples: ")
    print("netcat.py -t 192.168.0.1 -p 5555 -l -c")
    print("netcat.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe")
    print("netcat.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\"")
    print("echo 'ABCDEFGHI' | ./netcat.py -t 192.168.11.12 -p 135")
    sys.exit(0)


def client_sender(buffer):
    print("In client_sender")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # connect to target host
        client.connect((target, port))

        if len(buffer):
            client.send(buffer)

        while True:
            # now wait for data back
            recv_len = 1
            response = ""

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break

            print(response)

            # Wait for more input
            buffer = input("")
            buffer += "\n"

            # Send it off
            client.send(buffer)
    except:
        print("[*] Exception! Exiting....")
        # Tear down the connnection
        client.close()


def server_loop():
    print("In server_loop")
    global target
    # If no target is defined, we listen on all interfaces
    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        # Spin off a thread to handle our new client
        client_thread = threading.Threading(target=client_handler, args=(client_socket,))
        client_thread.start()


def run_command(command):
    print("In run_command")
    # Trim the new line
    command = command.rstrip()

    # Run the command and get the output back
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute command.\r\n"
    # Send the output back to the client
    return output


def client_handler(client_socket):
    print("In client_handler")
    global upload
    global execute
    global command

    # Check for upload
    if len(upload_destination):
        # Read in all of the bytes and write to our destination
        file_buffer = ""

        # Keep reading data until none is available
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            else:
                file_buffer += data

        # Now we take these bytes and try to write them out
        try:
            file_descriptor = open(upload_destintation, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            # Acknowledge that we wrote the file out
            client_socket.send("Successfully saved file to %s\r\n" % upload_destination)
        except:
            client_socket.send("Failed to save file to %s\r\n" %
                               upload_destination)

    # Check for command execution
    if len(execute):
        # Run the command
        output = run_command(execute)
        client_socket.send(output)

    # Goto another loop if a command shell was requested
    if command:
        print("CommandShell is true ")
        while True:
            # Show a simple prompt
            client_socket.send("<BHP:#> ")
            # Receieve until we see a linefeed (enter key)
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)

            # Send back the command output
            response = run_command(cmd_buffer)

            # Send back the response
            client_socket.send(response)
    else:
        print("CommandShell is false")


def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()

    # Read the commandline options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hel:t:p:cu:",
                                   ["help", "listen", "execute", "target", "port", "command", "upload"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        if o in ("-l", "--listen"):
            print("listen enabled")
            listen = True
        if o in ("-e", "--execute"):
            execute = a
        if o in ("-c", "--commandshell"):
            print("CommandShell enabled")
            command = True
        if o in ("-t", "--target"):
            target = a
        if o in ("-p", "--port"):
            port = int(a)
        # else:
        #     assert False, "Unhandled Option!"

    # Are we going to listen or just sned data from stdin?"
    if not listen and len(target) and port > 0:
        # Read in the buffer from the commandline
        # this will block, so send ctrl-D if not sending input
        # to stdin
        buffer = sys.stdin.read()

        # send data off
        client_sender(buffer)
        # we are going to listen and potentially
        # upload things, execute commands, and drop a shell back
        # depending on our command line options above
        if listen:
            server_loop()


main()