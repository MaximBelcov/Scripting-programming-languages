import socket

def start_udp_client(host='127.0.0.1', port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        while True:
            message = input("Введите сообщение для отправки или 'end' для завершения работы сервера: ")
            client_socket.sendto(message.encode('utf-8'), (host, port))
            if message.strip().lower() == "end":

                print("Клиент завершает работу.")

                break
            data, server = client_socket.recvfrom(1024)

            print(f"Получен ответ от сервера: {data.decode('utf-8')}")

if __name__ == "__main__":
    start_udp_client()