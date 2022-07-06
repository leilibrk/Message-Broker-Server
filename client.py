import json
import socket
import sys

HOST = sys.argv[1]
PORT = int(sys.argv[2])
conn = None


def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    return s


def isValid(cmd):
    if cmd == 'subscribe' or cmd == 'publish' or cmd == 'ping':
        return True
    else:
        return False


def listen():
    # conn.settimeout(10)
    while True:
        data = conn.recv(1024)
        if not data:
            continue
        decode_data = data.decode("utf-8")
        json_data = json.loads(decode_data)
        if json_data['cmd'] == 'SubAck':
            topics = json_data['topics']
            print('subscribing on ' + ' '.join(str(t) for t in topics))
        elif json_data['cmd'] == 'PubAck':
            print('your message published successfully')
        elif json_data['cmd'] == 'Message':
            topic = json_data['topic']
            message = json_data['message']
            print(topic + " : " + message)
        elif json_data['cmd'] == 'ping':
            pong_msg = {"cmd": "pong"}
            json_msg = json.dumps(pong_msg)
            conn.send(bytes(json_msg, encoding="utf-8"))
        elif json_data['cmd'] == 'pong':
            print('pong received successfully')
        else:
            print("invalid!")


conn = connect()
global command
command = sys.argv[3]
if not isValid(command):
    print("Wrong command!")
    exit(-1)
inputs = sys.argv[4:]
if command == 'publish':
    topic = inputs[0]
    message = inputs[1]
    msg = {"cmd": "publish", "topic": topic, "message": message}
    json_msg = json.dumps(msg)
    conn.send(bytes(json_msg, encoding="utf-8"))
elif command == 'subscribe':
    msg = {"cmd": "subscribe", "topics": inputs}
    json_msg = json.dumps(msg)
    conn.send(bytes(json_msg, encoding="utf-8"))
elif command == 'ping':
    ping_msg = {"cmd": "ping"}
    json_msg = json.dumps(ping_msg)
    conn.send(bytes(json_msg, encoding="utf-8"))
try:
    print("listen")
    listen()
except socket.error:
    print("Socket error")
