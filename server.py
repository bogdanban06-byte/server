import socket
import threading
import pickle
import random

# CONFIGURARE SERVER
PORT = 5555  # Portul intern pentru Railway
clients = []
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
    # Trimitem datele de start imediat după conectare
    try:
        conn.send(pickle.dumps({"id": player_id, "cuv": game_state["cuv"]}))
    except:
        return

    while True:
        try:
            data_raw = conn.recv(4096)
            if not data_raw:
                break
            
            data = pickle.loads(data_raw)
            
            if data["action"] == "guess":
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
                # Logica simplă de resetare runda (opțional se poate extinde)
                game_state["ghicite"] = []
                game_state["greseli"] = 0
                game_state["cuv"] = random.choice(cuvinte_posibile)

            # Trimitem starea actualizată tuturor
            msg = pickle.dumps(game_state)
            for c in clients:
                try:
                    c.send(msg)
                except:
                    clients.remove(c)
        except:
            break

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('0.0.0.0', PORT))
s.listen()
print(f"Server pornit pe portul {PORT}...")

while True:
    conn, addr = s.accept()
    if len(clients) < 2:
        player_id = len(clients) + 1
        clients.append(conn)
        print(f"Jucător {player_id} conectat de la {addr}")
        threading.Thread(target=handle_client, args=(conn, player_id)).start()