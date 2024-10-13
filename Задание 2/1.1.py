import socket

def start_tcp_server(host='127.0.0.1', port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))

        print(f"Сервер запущен на {host}:{port} и ожидает подключения...")

        server_socket.listen(1)
        conn, addr = server_socket.accept()
        with conn:
            
            print(f"Подключен клиент: {addr}")

            while True:
                data = conn.recv(1024)
                if not data:
                    break

                print(f"Получено сообщение от клиента: {data.decode('utf-8')}")
                
                conn.sendall(data)

if __name__ == "__main__":
    start_tcp_server()