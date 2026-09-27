import os
import socket

from shared import (
    send_message,
    recv_message,
    recv_exact
)


# Server connection settings.
HOST = "127.0.0.1"
PORT = 12345


def upload_file(client_socket):
    """Send a file from the client to the server."""

    # Ask the user which file should be uploaded.
    filename = input(
        "Enter the filename to upload: "
    )

    # Check that the requested file exists locally.
    if not os.path.isfile(filename):

        print("File not found.")

        return

    # Use only the filename rather than allowing a path
    # to be sent to the server.
    filename_bytes = os.path.basename(
        filename
    ).encode()

    # Determine the size of the file before transferring it.
    file_size = os.path.getsize(
        filename
    )

    # Tell the server that the next operation is an upload.
    send_message(
        client_socket,
        "upload"
    )

    # Send the filename length as a fixed 4-byte field.
    client_socket.sendall(
        f"{len(filename_bytes):04d}".encode()
    )

    # Send the filename itself.
    client_socket.sendall(
        filename_bytes
    )

    # Send the file size as a fixed 8-byte field.
    # The server uses this value to know when the transfer
    # is complete without relying on the TCP connection closing.
    client_socket.sendall(
        f"{file_size:08d}".encode()
    )

    print(
        f"Uploading {filename}..."
    )

    print(
        f"File size: {file_size} bytes"
    )

    # Open the file in binary mode so any file type can
    # be transferred, not just text files.
    with open(
        filename,
        "rb"
    ) as file:

        bytes_sent = 0

        while True:

            # Read the file in 4 KB chunks.
            chunk = file.read(4096)

            # An empty chunk means the end of the file.
            if not chunk:
                break

            # Send the current chunk to the server.
            client_socket.sendall(
                chunk
            )

            bytes_sent += len(chunk)

    print(
        f"Upload complete: "
        f"{bytes_sent} bytes sent."
    )

    # Receive the server's confirmation.
    response = recv_message(
        client_socket
    )

    print(
        f"Server: {response}"
    )


def download_file(client_socket):
    """Download a file from the server."""

    # Ask the user which file should be downloaded.
    filename = input(
        "Enter the filename to download: "
    )

    # Send only the filename rather than a complete path.
    filename_bytes = os.path.basename(
        filename
    ).encode()

    # Tell the server that the next operation is a download.
    send_message(
        client_socket,
        "download"
    )

    # Send the filename length.
    client_socket.sendall(
        f"{len(filename_bytes):04d}".encode()
    )

    # Send the filename.
    client_socket.sendall(
        filename_bytes
    )

    # Receive the server's response indicating whether
    # the requested file exists.
    status = recv_message(
        client_socket
    )

    if status == "NOT_FOUND":

        print(
            "File not found on server."
        )

        return

    if status != "FOUND":

        print(
            "Unexpected server response."
        )

        return

    # Receive the file size from the server.
    file_size = int(
        recv_exact(
            client_socket,
            8
        ).decode()
    )

    print(
        f"Downloading {filename} "
        f"({file_size} bytes)..."
    )

    # Save the downloaded file using a different filename
    # so it does not overwrite a local file with the same name.
    download_path = (
        f"downloaded_{os.path.basename(filename)}"
    )

    bytes_received = 0

    # Open the destination file in binary write mode.
    with open(
        download_path,
        "wb"
    ) as file:

        while bytes_received < file_size:

            # Calculate how many bytes are still expected.
            remaining = (
                file_size -
                bytes_received
            )

            # Receive up to 4 KB at a time.
            data = client_socket.recv(
                min(4096, remaining)
            )

            # Detect an unexpected server disconnect.
            if not data:

                raise ConnectionError(
                    "Server disconnected "
                    "during download."
                )

            # Write the received data to the local file.
            file.write(
                data
            )

            bytes_received += len(data)

    print(
        f"Download complete: "
        f"{bytes_received} bytes received."
    )


def start_client():
    """Start the TCP file transfer client."""

    # Create a TCP socket using IPv4.
    client_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    # Connect to the file transfer server.
    client_socket.connect(
        (HOST, PORT)
    )

    print(
        "Connected to server."
    )

    # Keep the connection open so the client can perform
    # multiple operations without reconnecting each time.
    while True:

        print(
            "\n1. Send message"
        )

        print(
            "2. Upload file"
        )

        print(
            "3. Download file"
        )

        print(
            "4. Exit"
        )

        choice = input(
            "Enter your choice: "
        )

        if choice == "1":

            # Send a normal text message to the server.
            message = input(
                "Message: "
            )

            send_message(
                client_socket,
                message
            )

            # Allow the user to exit by typing "exit"
            # as a message.
            if message.lower() == "exit":

                break

            # Receive the server's response.
            response = recv_message(
                client_socket
            )

            print(
                f"Server response: "
                f"{response}"
            )

        elif choice == "2":

            # Start a file upload.
            upload_file(
                client_socket
            )

        elif choice == "3":

            # Start a file download.
            download_file(
                client_socket
            )

        elif choice == "4":

            # Tell the server that the client is disconnecting.
            send_message(
                client_socket,
                "exit"
            )

            break

        else:

            print(
                "Invalid choice."
            )

    # Close the client socket when finished.
    client_socket.close()

    print(
        "Disconnected from server."
    )


if __name__ == "__main__":
    start_client()
