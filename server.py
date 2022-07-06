import json
import socket
import threading
import time

HOST = '127.0.0.1'
PORT = 1373
clients = {}
subscribed_client_topics = {}


def subscribe(topics, conn):
    for t in topics:
        if t in subscribed_client_topics:
            if conn not in subscribed_client_topics[t]:
                subscribed_client_topics[t].append(conn)
        else:
            subscribed_client_topics[t] = [conn]
    print(subscribed_client_topics)
    msg = {"cmd": "SubAck", "topics": topics}
    json_msg = json.dumps(msg)
    conn.send(bytes(json_msg, encoding="utf-8"))  # subscribe was successful


def publish(topic, message, conn):
    msg = {"cmd": "PubAck"}
    json_msg = json.dumps(msg)
    conn.send(bytes(json_msg, encoding="utf-8"))  # publish was successful

    pub_msg = {"cmd": "Message", "topic": topic, "message": message}
    json_pub_msg = json.dumps(pub_msg)
    for c in subscribed_client_topics[topic]:
        try:
            c.send(bytes(json_pub_msg, encoding="utf-8"))
        except:
            disconnect_client(c)


def ping(conn):
    ping_msg = {"cmd": "ping"}
    json_msg = json.dumps(ping_msg)
    data = bytes(json_msg, encoding="utf-8")
    conn.send(data)


def pong(conn):
    pong_msg = {"cmd": "pong"}
    json_msg = json.dumps(pong_msg)
    data = bytes(json_msg, encoding="utf-8")
    conn.send(data)


def command_handler(data, conn):
    if data["cmd"] == "subscribe":
        subscribe(data["topics"], conn)
    if data["cmd"] == "publish":
        publish(data["topic"], data["message"], conn)
    if data["cmd"] == "ping":
        pong(conn)
    if data["cmd"] == "pong":
        clients[conn] = 0


def handler(conn, addr):
    print('Connected by', addr)
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                continue
            data = data.decode("utf-8")
            data = json.loads(data)
            command_handler(data, conn)
        except:
            disconnect_client(conn)
            print('Disconnected by', addr)
            break


def disconnect_client(c):
    for t in subscribed_client_topics:
        if c in subscribed_client_topics[t]:
            subscribed_client_topics[t].remove(c)
    clients.pop(c)
    c.close()


def ping_all():
    for c in clients:
        if clients[c] == 3:
            disconnect_client(c)
        else:
            clients[c] += 1
            ping(c)
    print(clients)
    time.sleep(10)
    ping_all()


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()
threading.Thread(target=ping_all).start()
while True:
    conn, addr = s.accept()
    clients[conn] = 0
    threading.Thread(target=handler, args=(conn, addr)).start()
