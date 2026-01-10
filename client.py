import socket
import sys
import threading


class Client(object):

    def __init__(self):
        self._host = "localhost"
        self._port = 5500
        self._client_socket = socket.socket()
        self.active_users = []

    def start_connection_client(self):
        """
        Attempt to connect to the server
        """
        try:
            self._client_socket.connect((self._host, self._port))
        except Exception as e:
            print(f"[!][start_connection_client] Error connecting to server: {e}")
            sys.exit()
        print("\n" + "=" * 50)
        print(" WELCOME TO THE CHAT ROOM")
        print("=" * 50 + "\n")
        client_name = input("Enter your chat name: ").strip()
        if not client_name:
            print("Enter a vaild name. Exit from chat")
            self._client_socket.close()
            return

        try:
            self._client_socket.send(client_name.encode())
        except:
            print(f"[!][start_connection_client] Failed to send name to server")
            self._client_socket.close()
            return


        message_sender_thread = threading.Thread(target=self.receive_message, args=(self._client_socket,))
        message_sender_thread.daemon = True
        message_sender_thread.start()
        self.send_messages(self._client_socket, client_name)
        self._client_socket.close()
        print("[*][start_connection_client] Disconnected successfully")

    def send_messages(self, client_socket, client_name):
        print(f"\n------ Welcome {client_name} ------")
        print("The format to send message: [RelevantClient]:[Message]")
        print("To disconnect enter 'QUIT'")
        while True:
            try:
                message = input()
                if message.upper() == 'QUIT':
                    client_socket.send("".encode())
                    break

                client_socket.send(message.encode())

            except Exception as e:
                print(f"[!][send_messages] Error sending message: {e}")
                break

    def receive_message(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024).decode()
                if not data:
                    print("[!][receive_message] Connection closed by server")
                    break

                if data.startswith("USERS_LIST:"):
                    users_str = data.split(":", 1)[1]
                    if users_str.strip():
                        new_users = [name.strip() for name in data.split(",") if name.strip()]
                    else:
                        new_users = []
                    self.active_users = new_users
                    # self.draw_interface()
                    continue

                if data == "CONNECTED":
                    print("[*] Successfully connected to the chat server")
                    continue
                print(f"\n {data}")
            except ConnectionResetError:
                print(f"[!][send_messages] Connection to server lost.")
                break
            except Exception as e:
                print(f"[!][send_messages] Error: {e}")
                break

        client_socket.close()


if __name__ == "__main__":
    my_client = Client()
    my_client.start_connection_client()
