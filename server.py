import socket
import sys
import threading


class Server(object):

    def __init__(self):
        self._host = "127.0.0.1"
        self._port = 5500
        self._server = socket.socket()
        self.clients = {}
        self.lock = threading.Lock()

    def start(self):
        """

        """
        try:
            self._server.bind((self._host, self._port))
            self._server.listen(10)
            print(f"[*][start] Server listening on {self._host}:{self._port}")
        except Exception as e:
            print(f"[!][start] Error starting server: {e}")
            sys.exit(1)

        while True:
            try:
                client_socket, addr = self._server.accept()
                print(f"[*][start] New connection from: {addr}")

                client_thread = threading.Thread(target=self.handle_connection, args=(client_socket, addr))
                client_thread.start()
            except Exception as e:
                print(f"[!][start] Error accepting connection: {e}")
                break
        self._server.close()

    def handle_connection(self, client_socket, addr):
        try:
            client_name = client_socket.recv(1024).decode().strip()
            if not client_name:
                client_socket.close()
                return
            with self.lock:
                self.clients[client_name] = client_socket
            client_socket.send("CONNECTED TO THE CHAT\n".encode())
            self.broadcast_user_list()
            self.handle_client_messages(client_name, client_socket)

        except Exception as e:
            print(f"[!][handle_connection] Error during connection setup for {addr}: {e}")
            client_socket.close()
            if client_name in self.clients:
                with self.lock:
                    del self.clients[client_name]
                print(f"[!][handle_connection] Client '{client_name}' removed from list of clients.")

    def handle_client_messages(self, sender_name, client_socket):
        """
        After the client registered to chat- choose the relevant client
        to chat with him
        """
        while True:
            try:
                data = client_socket.recv(1024).decode()
                if not data:
                    break

                if ":" in data:
                    relevant_client, message = data.split(":", 1)
                    relevant_client = relevant_client.strip()
                    message = message.strip()

                    self.send_private_message(sender_name, relevant_client, message)
                else:
                    client_socket.send("[!][handle_client_messages][Server]: Invalid message format. The corrent format [RelevantClient]:[Message]".encode())

            except ConnectionResetError:
                break
            except Exception as e:
                print(f"[!][handle_client_messages] Error from {sender_name}: {e}")
                break

        print(f"[*][handle_client_messages] Client '{sender_name}' disconnected from chat")
        self.disconnect_client(sender_name, client_socket)

    def broadcast_user_list(self):
        with self.lock:
            payload = f'USERS LIST: {",".join(self.clients.keys())}'.encode()
            for name, curr_socket in list(self.clients.items()):
                try:
                    curr_socket.sendall(payload)
                except Exception as e:
                    print(f"[!][broadcast_user_list] failed to send user list to {name}: {e}")

    def send_private_message(self, sender_name, relevant_client, message):
        with self.lock:
            if relevant_client in self.clients:
                relevant_socket = self.clients[relevant_client]
                full_message = f"{sender_name} >>> {message}"

                try:
                    relevant_socket.sendall(full_message.encode())
                    print(f"[*][send_private_message] Message from {sender_name} to {relevant_client} sent")
                except Exception as e:
                    print(f"[!][send_private_message] Error sending message to {relevant_client}: {e}")
                    self.disconnect_client(relevant_client, relevant_socket)

            else:
                sender_socket = self.clients.get(sender_name)
                if sender_socket:
                    error_msg = f"Server: client '{relevant_client}' not found"
                    sender_socket.send(error_msg.encode())
                    print(f"[!][send_private_message] Error: client '{relevant_client}' not found for message from {sender_name}")

    def disconnect_client(self, client_name, client_socket):
        try:
            client_socket.close()
        except:
            pass

        removed = False
        with self.lock:
            if client_name in self.clients:
                del self.clients[client_name]
                removed = True
                print(f"[*][disconnect_client] Client '{client_name}' removed from list of clients. Total clients: {len(self.clients)}")

        if removed:
            self.broadcast_user_list()


if __name__ == "__main__":
    my_server = Server()
    try:
        my_server.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        sys.exit()