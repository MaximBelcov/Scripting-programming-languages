import socket

def start_udp_server(host='127.0.0.1', port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind((host, port))

        print(f"UDP сервер запущен на {host}:{port} и ожидает сообщений...")

        while True:
            data, addr = server_socket.recvfrom(1024)
            message = data.decode('utf-8')

            print(f"Получено сообщение от клиента {addr}: {message}")
            
            if message.strip().lower() == "end":

                print("Получена команда остановки сервера. Завершение работы...")

                break
            server_socket.sendto(data, addr)

    print("Сервер остановлен.")

if __name__ == "__main__":
    start_udp_server()