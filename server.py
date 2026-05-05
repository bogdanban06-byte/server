import socket
import pickle
import threading
import os

# Portul este luat automat de la Railway
PORT = int(os.environ.get("PORT", 5555))
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', PORT))
server.listen(2)

clients = []
# Starea jocului pe care serverul o va sincroniza
game_state = {
    "stare": "MENU", "cuv": "", "ghicite": [], "greseli": 0,
    "s1": 0, "s2": 0, "l1": 0, "l2": 0, "c1": 0, "c2": 0, "rand": True
}

def handle_client(conn):
    global game_state
    clients.append(conn)
    while True:
        try:
            data = conn.recv(4096)
            if not data: break
            
            # Primim date de la un jucător și actualizăm starea
            received = pickle.loads(data)
            # Dacă primim o literă sau o stare nouă, o salvăm în game_state
            if isinstance(received, dict): game_state.update(received)
            
            # Trimitem starea actualizată tuturor
            for client in clients:
                try: client.send(pickle.dumps(game_state))
                except: clients.remove(client)
        except: break
    conn.close()

print(f"Server activ pe portul {PORT}")
while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn,)).start()