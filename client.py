import socket
import threading
from cryptography.fernet import Fernet

def receive_messages(client_socket, fernet):
    while True:
        try:
            message = client_socket.recv(1024)
            if message:
                decrypted_message = fernet.decrypt(message).decode('utf-8')
                print(decrypted_message)
            else:
                break
        except Exception as e:
            print(f"Ошибка: {e}")
            break

def send_messages(client_socket, fernet):
    while True:
        message = input()
        client_socket.send(fernet.encrypt(message.encode('utf-8')))

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('176.99.161.15', 5555))
    key = client_socket.recv(1024)
    fernet = Fernet(key)

    nickname = input("Введите ваш никнейм: ")
    client_socket.send(nickname.encode('utf-8'))

    threading.Thread(target=receive_messages, args=(client_socket, fernet)).start()
    send_messages(client_socket, fernet)

start_client()
