import socket
import threading
import pickle
import random
import time

# CONFIGURARE SERVER
PORT = 5555 
clients = {} # Folosim dictionar pentru a tine evidenta ID-urilor
cuvinte_posibile = ["PYTHON", "RAILWAY", "RETEA", "CLIENT", "SERVER", "DINOSAUR", "TEHNOLOGIE"]

# Starea globală a jocului
game_state = {
    "cuv": random.choice(cuvinte_posibile),
    "ghicite": [],
    "greseli": 0,
    "s1": 0, "s2": 0,
    "l1": 0, "l2": 0,
    "rand_la_player": 1,
    "stare": "PLAYING"
}

def handle_client(conn, player_id):
    global game_state
    
    print(f"[SERVER] Trimit date initiale catre Player {player_id}")
    try:
        # Oferim clientului un moment sa treaca de faza de conectare
        time.sleep(0.5) 
        conn.send(pickle.dumps({"id": player_id, "cuv": game_state["cuv"]}))
    except Exception as e:
        print(f"[EROARE] Trimitere initiala esuata: {e}")
        return

    while True:
        try:
            data_raw = conn.recv(4096)
            if not data_raw:
                break
            
            data = pickle.loads(data_raw)
            
            if data.get("action") == "guess":
                l = data["letter"]
                if l not in game_state["ghicite"]:
                    game_state["ghicite"].append(l)
                    if l in game_state["cuv"]:
                        if player_id == 1: game_state["l1"] += game_state["cuv"].count(l)
                        else: game_state["l2"] += game_state["cuv"].count(l)
                    else:
                        game_state["greseli"] += 1
                    
                    # Schimbăm rândul
                    game_state["rand_la_player"] = 2 if player_id == 1 else 1
            
            # Verificare final runda
            cuvant_complet = all(c in game_state["ghicite"] for c in game_state["cuv"])
            if game_state["greseli"] >= 6 or cuvant_complet:
                time.sleep(1) # Pauza scurta inainte de cuvant nou
                game_state["ghicite"] = []
                game_state["greseli"] = 0
                game_state["cuv"] = random.choice(cuvinte_posibile)

            # Trimitem starea actualizată tuturor jucatorilor activi
            msg = pickle.dumps(game_state)
            for pid, c_conn in list(clients.items()):
                try:
                    c_conn.send(msg)
                except:
                    del clients[pid]
        except:
            break

    print(f"[SERVER] Player {player_id} s-a deconectat.")
    if player_id in clients:
        del clients[player_id]
    conn.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Permite repornirea rapida a portului
s.bind(('0.0.0.0', PORT))
s.listen()
print(f"[SERVER] Ruleaza pe portul {PORT}...")

while True:
    conn, addr = s.accept()
    # Atribuim primul ID liber (1 sau 2)
    if 1 not in clients:
        p_id = 1
    elif 2 not in clients:
        p_id = 2
    else:
        print("[SERVER] Server plin, resping conexiunea.")
        conn.close()
        continue

    clients[p_id] = conn
    print(f"[SERVER] Jucător {p_id} conectat: {addr}")
    threading.Thread(target=handle_client, args=(conn, p_id), daemon=True).start()