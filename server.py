import os
import socket
import threading

from shared import (
    send_message,
    recv_message,
    recv_exact
)

# Server connection settings.
HOST = "127.0.0.1"
PORT = 12345

def receive_file(client_socket):
    """Receive a file from a connected client."""

    # Receive the filename length.
    filename_length = int(
        recv_exact(
            client_socket,
            4
        ).decode()
    )

    # Receive the filename using the known length.
    filename = recv_exact(
        client_socket,
        filename_length
    ).decode()

    # Remove any directory components from the filename.
    # This prevents directory traversal such as ../../file.txt.
    filename = os.path.basename(
        filename
    )

    # Receive the file size.
    file_size = int(
        recv_exact(
            client_socket,
            8
        ).decode()
    )

    # Make sure the server storage directory exists.
    os.makedirs(
        "server_files",
        exist_ok=True
    )

    # Build the path where the uploaded file will be stored.
    filepath = os.path.join(
        "server_files",
        filename
    )

    print(
        f"Receiving file: {filename}"
    )

    print(
        f"File size: {file_size} bytes"
    )

    bytes_received = 0

    # Open the destination file in binary write mode.
    with open(
        filepath,
        "wb"
    ) as file:

        while bytes_received < file_size:

            # Calculate how many bytes are still expected.
            remaining = (
                file_size -
                bytes_received
            )

            # Receive the file in chunks of up to 4 KB.
            data = client_socket.recv(
                min(4096, remaining)
            )

            # Detect if the client disconnects before
            # the complete file has been received.
            if not data:

                raise ConnectionError(
                    "Client disconnected "
                    "during file transfer."
                )

            # Write the received bytes to disk.
            file.write(
                data
            )

            bytes_received += len(data)

    print(
        f"File received successfully: "
        f"{filename}"
    )

    # Confirm successful upload to the client.
    send_message(
        client_socket,
        f"Upload successful: {filename}"
    )


def send_file(client_socket):
    """Send a requested file to a connected client."""

    # Receive the filename length.
    filename_length = int(
        recv_exact(
            client_socket,
            4
        ).decode()
    )

    # Receive the filename.
    filename = recv_exact(
        client_socket,
        filename_length
    ).decode()

    # Remove any directory components from the filename.
    filename = os.path.basename(
        filename
    )

    # Build the path to the requested server file.
    filepath = os.path.join(
        "server_files",
        filename
    )

    # Check whether the requested file exists.
    if not os.path.isfile(filepath):

        send_message(
            client_socket,
            "NOT_FOUND"
        )

        return

    # Determine the file size before sending the file.
    file_size = os.path.getsize(
        filepath
    )

    # Tell the client that the file exists.
    send_message(
        client_socket,
        "FOUND"
    )

    # Send the file size as a fixed 8-byte field.
    client_socket.sendall(
        f"{file_size:08d}".encode()
    )

    print(
        f"Sending file: {filename}"
    )

    print(
        f"File size: {file_size} bytes"
    )

    # Open the requested file in binary read mode.
    with open(
        filepath,
        "rb"
    ) as file:

        bytes_sent = 0

        while True:

            # Read the file in 4 KB chunks.
            chunk = file.read(4096)

            # Stop when the entire file has been read.
            if not chunk:
                break

            # Send the current chunk to the client.
            client_socket.sendall(
                chunk
            )

            bytes_sent += len(chunk)

    print(
        f"File sent successfully: "
        f"{filename}"
    )


def handle_client(
    client_socket,
    client_address
):
    """
    Handle communication with one connected client.

    Each client is handled by a separate thread, allowing
    multiple clients to use the server at the same time.
    """

    print(
        f"Client connected: "
        f"{client_address}"
    )

    try:

        while True:

            # Receive one complete application-level message.
            message = recv_message(
                client_socket
            )

            # Handle client disconnection.
            if message.lower() == "exit":

                print(
                    f"Client requested disconnect: "
                    f"{client_address}"
                )

                break

            # Start a file upload.
            elif message.lower() == "upload":

                receive_file(
                    client_socket
                )

            # Start a file download.
            elif message.lower() == "download":

                send_file(
                    client_socket
                )

            # Handle normal text messages.
            else:

                print(
                    f"Message from "
                    f"{client_address}: "
                    f"{message}"
                )

                response = (
                    f"Server received: "
                    f"{message}"
                )

                send_message(
                    client_socket,
                    response
                )

    except ConnectionError as error:

        print(
            f"Connection error with "
            f"{client_address}: {error}"
        )

    finally:

        # Always close the client socket when finished.
        client_socket.close()

        print(
            f"Client disconnected: "
            f"{client_address}"
        )


def start_server():
    """Start the multi-client TCP file transfer server."""

    # Create an IPv4 TCP socket.
    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    # Allow the server to reuse the address immediately
    # after restarting.
    server_socket.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    # Bind the socket to the configured host and port.
    server_socket.bind(
        (HOST, PORT)
    )

    # Allow up to five pending connections in the queue.
    server_socket.listen(5)

    print(
        f"Server listening on "
        f"{HOST}:{PORT}"
    )

    print(
        "Waiting for clients..."
    )

    while True:

        # Wait for a new client connection.
        client_socket, client_address = (
            server_socket.accept()
        )

        # Create a separate thread for each client.
        client_thread = threading.Thread(
            target=handle_client,
            args=(
                client_socket,
                client_address
            )
        )

        # Start handling the client immediately.
        client_thread.start()

        print(
            f"Active client threads: "
            f"{threading.active_count() - 1}"
        )


if __name__ == "__main__":
    start_server()
