import struct

def send_message(client_socket, message):
    """
    Send a length-prefixed message over TCP.

    TCP is a byte stream, so messages are not automatically
    separated. A 4-byte header containing the message length
    allows the receiver to determine exactly how many bytes
    belong to the message.
    """

    # Convert the message from a string to bytes.
    data = message.encode()

    # Pack the message length into 4 bytes using network
    # byte order (big-endian).
    header = struct.pack("!I", len(data))

    # Send the length header followed by the message.
    client_socket.sendall(header + data)


def recv_message(client_socket):
    """
    Receive one complete length-prefixed message from TCP.
    """

    # First receive the 4-byte message length.
    header = recv_exact(
        client_socket,
        4
    )

    # Convert the 4-byte header back into an integer.
    message_length = struct.unpack(
        "!I",
        header
    )[0]

    # Receive exactly the number of bytes specified by
    # the message length.
    data = recv_exact(
        client_socket,
        message_length
    )

    # Convert the received bytes back into a string.
    return data.decode()


def recv_exact(client_socket, size):
    """
    Receive exactly 'size' bytes from a TCP socket.

    A single recv() call is not guaranteed to return all
    requested bytes because TCP is a continuous byte stream.
    This function continues receiving until the required
    number of bytes has been collected.
    """

    data = b""

    while len(data) < size:

        # Request only the number of bytes still needed.
        chunk = client_socket.recv(
            size - len(data)
        )

        # An empty result means the connection was closed.
        if not chunk:

            raise ConnectionError(
                "Connection closed while receiving data."
            )

        # Add the received bytes to the data collected so far.
        data += chunk

    return data
