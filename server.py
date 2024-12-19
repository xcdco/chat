import socket
import threading
from cryptography.fernet import Fernet

def generate_key():
    return Fernet.generate_key()

def handle_client(client_socket, clients, fernet, nicknames):
    nickname = client_socket.recv(1024).decode('utf-8')
    nicknames[nickname] = client_socket
    print(f"{nickname} подключен.")
    
    in_private_chat = None

    while True:
        try:
            message = client_socket.recv(1024)
            if message:
                decrypted_message = fernet.decrypt(message).decode('utf-8')
                print(f"Получено сообщение от {nickname}: {decrypted_message}")

                if decrypted_message == "/list":
                    participants = ', '.join(nicknames.keys())
                    client_socket.send(fernet.encrypt(f"Участники чата: {participants}".encode('utf-8')))
                elif decrypted_message.startswith("/pm"):
                    parts = decrypted_message.split(" ", 2)
                    if len(parts) < 3:
                        client_socket.send(fernet.encrypt("Используйте: /pm <ник> <сообщение>".encode('utf-8')))
                        continue
                    _, target_nickname, private_message = parts
                    if target_nickname in nicknames:
                        target_socket = nicknames[target_nickname]
                        target_socket.send(fernet.encrypt(f"Личное сообщение от {nickname}: {private_message}".encode('utf-8')))
                    else:
                        client_socket.send(fernet.encrypt(f"Пользователь {target_nickname} не найден.".encode('utf-8')))
                elif decrypted_message.startswith("/pc"):
                    parts = decrypted_message.split(" ", 1)
                    if len(parts) < 2:
                        client_socket.send(fernet.encrypt("Используйте: /pc <ник>".encode('utf-8')))
                        continue
                    _, target_nickname = parts
                    if target_nickname in nicknames:
                        client_socket.send(fernet.encrypt(f"Вы перешли в личный чат с {target_nickname}.".encode('utf-8')))
                        target_socket = nicknames[target_nickname]
                        target_socket.send(fernet.encrypt(f"{nickname} присоединился к личному чату.".encode('utf-8')))
                        in_private_chat = target_nickname
                    else:
                        client_socket.send(fernet.encrypt(f"Пользователь {target_nickname} не найден.".encode('utf-8')))
                elif decrypted_message.startswith("/exitpc"):
                    if in_private_chat:
                        client_socket.send(fernet.encrypt(f"Вы вышли из личного чата с {in_private_chat}.".encode('utf-8')))
                        target_socket = nicknames[in_private_chat]
                        target_socket.send(fernet.encrypt(f"{nickname} вышел из личного чата.".encode('utf-8')))
                        in_private_chat = None
                    else:
                        client_socket.send(fernet.encrypt(f"Вы не находитесь в личном чате.".encode('utf-8')))
                else:
                    if in_private_chat:
                        target_socket = nicknames[in_private_chat]
                        target_socket.send(fernet.encrypt(f"{nickname}: {decrypted_message}".encode('utf-8')))
                    else:
                        for client in clients:
                            if client != client_socket:
                                client.send(fernet.encrypt(f"{nickname}: {decrypted_message}".encode('utf-8')))
            else:
                break
        except Exception as e:
            print(f"Ошибка: {e}")
            break
    client_socket.close()
    if nickname in nicknames:
        del nicknames[nickname]

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('176.99.161.15', 5555))
    server_socket.listen(5)
    print("Сервер запущен и ожидает подключения...")

    clients = []
    nicknames = {}
    key = generate_key()
    fernet = Fernet(key)

    while True:
        client_socket, addr = server_socket.accept()
        clients.append(client_socket)
        client_socket.send(key)  
        client_thread = threading.Thread(target=handle_client, args=(client_socket, clients, fernet, nicknames))
        client_thread.start()

start_server()
