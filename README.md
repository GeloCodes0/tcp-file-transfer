# Multi-Client TCP File Transfer

A Python-based client-server application that uses TCP sockets to support **multiple simultaneous clients**, text messaging, and binary file uploads/downloads.

This project was developed as a portfolio project to demonstrate practical knowledge of **TCP networking, socket programming, application-layer protocol design, concurrency, and file transfer**.

---

## Features

* Multi-client TCP server
* Separate thread for each connected client
* Text messaging between client and server
* File uploads from client to server
* File downloads from server to client
* Binary file transfer using chunks
* Application-layer message framing
* File size-based transfer control
* Filename sanitisation
* Multiple operations over a single TCP connection
* Graceful client disconnection

---

## How It Works

The server listens for incoming TCP connections on:

```text
127.0.0.1:12345
```

When a client connects, the server creates a separate thread to handle that client.

```text
                    TCP CONNECTION
                         |
          +--------------+--------------+
          |              |              |
       Client 1       Client 2       Client 3
          |              |              |
       Thread 1        Thread 2        Thread 3
          |              |              |
          +--------------+--------------+
                         |
                    TCP SERVER
```

Each client can independently:

```text
1. Send message
2. Upload file
3. Download file
4. Exit
```

---

## TCP Application-Layer Framing

TCP provides a reliable byte stream, but it does not automatically separate individual application messages.

For example, sending:

```text
Hello
World
```

does not guarantee that the receiver will receive them as two separate messages.

To solve this, this project uses **length-prefixed messages**.

Each message is sent as:

```text
+----------------------+----------------------+
| 4-byte message size | Message data         |
+----------------------+----------------------+
```

The receiver first reads the 4-byte length and then reads exactly that number of bytes.

This prevents messages from becoming mixed together when multiple pieces of data are sent over the same TCP connection.

---

## File Transfer Protocol

File transfers use additional fixed-size fields.

### Upload

```text
Client
  |
  | Length-prefixed "upload" command
  |
  | 4-byte filename length
  |
  | Filename
  |
  | 8-byte file size
  |
  | File data in 4 KB chunks
  |
  v
Server
```

The server uses the file size to determine when the complete file has been received instead of relying on the TCP connection closing.

### Download

```text
Client
  |
  | Length-prefixed "download" command
  |
  | Filename
  |
  v
Server
  |
  | FOUND / NOT_FOUND
  |
  | File size
  |
  | File data in 4 KB chunks
  |
  v
Client
```

---

## Security Considerations

The project includes basic protections around file handling.

### Filename Sanitisation

Filenames are processed using:

```python
os.path.basename()
```

This removes directory components from filenames.

For example:

```text
../../secret.txt
```

is reduced to:

```text
secret.txt
```

This helps prevent directory traversal through uploaded or requested filenames.

### Binary File Handling

Files are opened using binary modes:

```python
"rb"
"wb"
```

This allows the application to transfer files without modifying their binary contents.

---

## Project Structure

```text
03-tcp-file-transfer/
│
├── server.py
├── client.py
├── shared.py
├── README.md
├── .gitignore
│
└── server_files/
```

### `server.py`

Contains the multi-client TCP server.

Responsibilities include:

* Accepting client connections
* Creating client threads
* Processing client commands
* Receiving uploaded files
* Sending requested files
* Handling client messages

### `client.py`

Contains the client application.

Responsibilities include:

* Connecting to the server
* Sending messages
* Uploading files
* Downloading files
* Handling user interaction

### `shared.py`

Contains common networking functions used by both the client and server.

The main functions are:

```python
send_message()
recv_message()
recv_exact()
```

`recv_exact()` ensures that the application receives the exact number of bytes required rather than assuming a single `recv()` call will return everything.

---

## Technologies Used

| Technology  | Purpose                     |
| ----------- | --------------------------- |
| Python      | Application development     |
| TCP sockets | Client-server communication |
| `socket`    | Network connections         |
| `threading` | Multi-client handling       |
| `struct`    | Message length encoding     |
| `os`        | File and path handling      |

---

## Requirements

* Python 3.x
* Windows, Linux, or macOS
* No external Python packages required

---

## Running the Server

Open a terminal in the project directory:

```powershell
cd 03-tcp-file-transfer
```

Start the server:

```powershell
python server.py
```

Expected output:

```text
Server listening on 127.0.0.1:12345
Waiting for clients...
```

---

## Running a Client

Open another terminal in the project directory:

```powershell
python client.py
```

The client should display:

```text
Connected to server.

1. Send message
2. Upload file
3. Download file
4. Exit
```

---

## Testing Multiple Clients

The server supports multiple simultaneous clients.

Start the server in one terminal:

```powershell
python server.py
```

Then open two or more additional terminals and run:

```powershell
python client.py
```

The server will create a separate thread for each connected client.

Example:

```text
Client connected: ('127.0.0.1', 62524)
Active client threads: 1

Client connected: ('127.0.0.1', 62527)
Active client threads: 2
```

Each client can then send messages or transfer files independently.

---

## Example File Transfer

Client:

```text
Enter your choice: 2
Enter the filename to upload: test.txt

Uploading test.txt...
File size: 67 bytes
Upload complete: 67 bytes sent.
Server: Upload successful: test.txt
```

Downloading:

```text
Enter your choice: 3
Enter the filename to download: test.txt

Downloading test.txt (67 bytes)...
Download complete: 67 bytes received.
```

---

## Lessons Learned

This project reinforced several important concepts in network programming:

* TCP is a byte stream rather than a message-based protocol.
* Application-layer framing is required when exchanging structured messages over TCP.
* `recv()` is not guaranteed to return all requested data.
* `sendall()` is useful when reliably transmitting application data.
* Threads can be used to handle multiple clients concurrently.
* File sizes can be used to control the boundaries of binary file transfers.
* File paths received from clients should be sanitised before being used.
* A well-designed protocol prevents messages and file data from becoming misaligned.

---

## Future Improvements

Possible future improvements include:

* TLS encryption for client-server communication
* User authentication
* File integrity verification using hashes
* File transfer progress indicators
* Configurable server host and port
* Connection limits
* Logging to a dedicated log file
* Improved error handling and protocol validation

---

## Disclaimer

This project was developed for educational and portfolio purposes to demonstrate networking and socket programming concepts.
