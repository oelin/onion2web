from socket import socket
from urllib.parse import urlparse
import socks


server_port = 8899
socks_port = 9050
recv_length = 4096

socks.set_default_proxy(socks.SOCKS5, '127.0.0.1', socks_port)
socksocket = socks.socksocket

server = socket()
server.bind(('localhost', server_port))
server.listen(5)


while 1:
    client, info = server.accept()
    client_request = str(client.recv(recv_length), 'utf-8')

    # Get the target URL.

    lines = client_request.split('\r\n')
    query = lines[0].split(' ')
    verb, url, version = query
    url = urlparse(url)

    # Extract the request headers (and body if present).

    headers_offset = 0 + len(lines[0])
    headers = client_request[headers_offset:]

    # Forward the request through Tor.

    new_query = f'{verb} {url.path} {version}' + headers
    new_socket = socksocket()
    new_socket.connect((url.hostname, url.port or 80))
    new_socket.sendall(new_query.encode())

    # Fetch the HTTP response.

    remote_response = b''
    chunk = new_socket.recv(recv_length)
    remote_response += chunk
    new_socket.close()

    # Send the response to the original client.

    client.send(remote_response)
    client.close()

    print(f'{lines[0]}')
