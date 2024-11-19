import socket
import json
import threading
from collections import defaultdict
import os
import time

# Constants
PORT = 3466
PORT2 = 3467
BUFFER_SIZE = 1024

# Get the hostname of the machine
hostname = socket.gethostname()

#lock to secure the access to the shared variables
lock = threading.Lock()

# receivers stopper
# stopper_receiver = True
# stopper_receiver_phase2 = True

# Data structures for phases
machines_list = []
local_words = []
received_words = defaultdict(int)

#phase 2 syncer
status_phase2 = {}
init_trigger = True

# Create a socket to listen for incoming connections for phase 1
server_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
for tentative in range(5):
        try:
            server_socket1.bind(('0.0.0.0', PORT))
            print(f"'{hostname}' : socket connected to {PORT} after {tentative + 1} trie(s).")
            break
        except OSError:
            if tentative < 4:
                # If the port is used, free it by using command kill
                print(f"'{hostname}' : port {PORT} is already in use. freeing it try number ({tentative + 1}/5)...")
                # Afficher avec print le PID du processus qui utilise le port
                pid = os.popen(f'lsof -t -i:{PORT}').read().strip()
                print(f"'{hostname}' : PID of process using port {PORT} : {pid}")
                if pid:
                    # Free the port and print the result of kill
                    os.system(f'kill -9 {pid}')
                    print(f"'{hostname}' : try of killing process {pid}.")
                else:
                    print(f"'{hostname}' : No process is using port {PORT}.")
                time.sleep(5)
            else:
                raise Exception(f"'{hostname}' : Impossible to connect socket to port {PORT} after 5 tries.")


# # Create a socket to listen for incoming connections for phase 2
# server_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# for tentative in range(5):
#         try:
#             server_socket2.bind(('0.0.0.0', PORT2))
#             print(f"'{hostname}' : socket connected to port {PORT2} after {tentative + 1} trie(s).")
#             break
#         except OSError:
#             if tentative < 4:
#                 # If the port is used, free it by using command kill
#                 print(f"'{hostname}' : port {PORT2} is already in use. freeing it try number ({tentative + 1}/5)...")
#                 # Afficher avec print le PID du processus qui utilise le port
#                 pid = os.popen(f'lsof -t -i:{PORT2}').read().strip()
#                 print(f"'{hostname}' : PID of process using port {PORT2} : {pid}")
#                 if pid:
#                     # Free the port and print the result of kill
#                     os.system(f'kill -9 {pid}')
#                     print(f"'{hostname}' : try of killing process {pid}.")
#                 else:
#                     print(f"'{hostname}' : No process is using port {PORT2}.")
#                 time.sleep(5)
#             else:
#                 raise Exception(f"'{hostname}' : Impossible to connect socket to port {PORT2} after 5 tries.")

# Start listening for incoming connections
server_socket1.listen(5)
print(f"[{hostname}] Server 1 listening on port {PORT}...")

# server_socket2.listen(5)
# print(f"[{hostname}] Server 2 listening on port {PORT2}...")

# def send_word_to_machine(machine, word):
#     """Send a single word to the target machine."""
#     try:
#         with socket.create_connection((machine, PORT)) as sock:
#             # Prepare the data packet
#             data = {
#                 'phase': 2,
#                 'word': word  # Send one word at a time
#             }
#             sock.sendall(json.dumps(data).encode('utf-8'))
#             response = sock.recv(BUFFER_SIZE)
#             print(f"[{hostname}] Response from {machine}: {response.decode('utf-8')}")
#     except Exception as e:
#         print(f"[{hostname}] Error sending word '{word}' to {machine}: {e}")


# def redistribute_words():
#     """Redistribute words to the appropriate machines during Phase 2."""
#     threads = []
#     for word in local_words:
#         target_machine_index = len(word) % len(machines_list)
#         target_machine = machines_list[target_machine_index]

#         if target_machine != hostname:  # Avoid sending to self
#             print(f"[{hostname}] [Phase 2] Sending word '{word}' to {target_machine}")
#             thread = threading.Thread(target=send_word_to_machine, args=(target_machine, word))
#             threads.append(thread)
#             thread.start()

#     for thread in threads:
#         thread.join()

def send_to_machine(machine, data, phase):
    """Send data to a machine."""
    # try:
    #     machines_list[machine].sendall(json.dumps(data).encode('utf-8'))
    # except Exception as e:
    #     print(f"[Phase {phase}] Error sending to {machine}: {e}")
    try:
        # establish connexion
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # connect to machine
        client_socket.connect((machine, PORT))

        # send data
        client_socket.sendall(json.dumps(data).encode('utf-8'))
    except Exception as e:
        print(f"[Phase {phase}] Error sending to {machine}: {e}")

def phase3():
    """print word counts."""
    print(f"[{hostname}] [Phase 3] Word counts: {received_words}")

def handle_client(client_socket, address):
    """Handle incoming connections and process data."""
    global machines_list, local_words, received_words, status_phase2, init_trigger

    try:
        # Receive data from the client
        data = client_socket.recv(BUFFER_SIZE).decode('utf-8')
        message = json.loads(data)

        # Phase 1: Receive list of machines and string part
        if message['phase'] == 1:
            machines_list = message['machines']
            local_words = message['string'].split()
            print(f"[{hostname}] [Phase 1] Received machines: {machines_list}")
            print(f"[{hostname}] [Phase 1] Local words: {local_words}")
            data = {
                'content': "finished phase 1"
            }
            client_socket.sendall(json.dumps(data).encode('utf-8'))
            if init_trigger == True :
                print(f"{hostname}:initializing syncer of phase 2")
                for machine in machines_list :
                    status_phase2[machine] = False
                init_trigger = False

            


        # Phase 2: Receive individual words from other machines
        elif message['phase'] == 2:
            word = message['content']
            if word == "start phase 2":
                # for machine in machines_list:
                #     if machine != hostname:
                        # try:
                        #     # Créer un socket TCP/IP
                        #     client_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            
                        #     # Se connecter à la machine
                        #     client_socket2.connect((machine, PORT))
                        #     print(f"{hostname}:Connected to machine {machine}")


                        #     # Vérifier si la connexion est établie
                        #     if client_socket2:
                        #         print(f"{hostname} [phase 2] : Connection to machine {machine} established successfully.")
                        #     else:
                        #         print(f"{hostname} [phase 2] : Failed to establish connection to machine {machine}.")
                            
                        #     # Stocker la connexion
                        #     machines_list[machine] = client_socket2
                            
                        # except Exception as e:
                        #     print(f"{hostname} [phase 2] Error connecting to machine {machine}: {e}")
                for word in local_words :
                    machine_number = len(word) % len(machines_list)
                    print(f"{hostname}:Sending word {word} to machine {machines_list[machine_number]}")
                    if machines_list[machine_number] != hostname:
                        data = {
                            'phase': 2,
                            'content': word
                        }
                        send_to_machine(machines_list[machine_number], data, 2)
                    else :
                        with lock :
                            received_words[word] += 1
                            print(f"[{hostname}] [Phase 2] claimed word: '{word}'")

            else :
                with lock :
                    received_words[word] += 1
                    print(f"[{hostname}] [Phase 2] received word: '{word}'")
                    
        elif message['phase'] == 3:
            print(f"{hostname} [phase 3] Received signal: {message['content']}")
            response = json.dumps(received_words)
            client_socket.sendall(response.encode('utf-8'))
            print(f"[{hostname}] [Phase 3] Sent word counts: {received_words}")

        # # Phase 3: Send word counts back
        # elif message['phase'] == 3:
        #     response = json.dumps(received_words)
        #     client_socket.sendall(response.encode('utf-8'))
        #     print(f"[{hostname}] [Phase 3] Sent word counts: {received_words}")

    except Exception as e:
        print(f"[{hostname}] Error handling client {address}: {e}")
    finally:
        client_socket.close()


def receiver():
    """Start a thread to listen for incoming words during Phase 1."""
    while True:
        client_socket, address = server_socket1.accept()
        print(f"[{hostname}] Connection established with {address}")
        client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
        client_thread.start()
        client_thread.join()
        client_socket.close()

# def receiver_phase2():
#     """Start a thread to listen for incoming words during Phase 2."""
#     global stopper_receiver_phase2
    
#     while stopper_receiver_phase2:
#         client_socket, address = server_socket2.accept()
#         print(f"[{hostname}] [Phase 2] Connection established with {address}")
#         client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
#         client_thread.start()

if __name__ == "__main__":
    try:
        print(f"[{hostname}] Starting the server...")
        receiver1 = threading.Thread(target=receiver, daemon=True)
        receiver1.start()
        # receiver1.join()
        
        while True :
            time.sleep(1)


    except KeyboardInterrupt:
        print(f"\n[{hostname}] Server shutting down.")
    except Exception as e:
        print(f"[{hostname}] Server error: {e}")
