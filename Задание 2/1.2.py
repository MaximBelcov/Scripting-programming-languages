import socket

def start_tcp_client(host='127.0.0.1', port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))

        print(f"Подключен к серверу {host}:{port}")
        
        message = input("Введите сообщение для отправки: ")
        client_socket.sendall(message.encode('utf-8'))
        data = client_socket.recv(1024)
        
        print(f"Получен ответ от сервера: {data.decode('utf-8')}")

if __name__ == "__main__":
    start_tcp_client()