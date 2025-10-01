import socket
import os
import hashlib

# Config
HOST = '0.0.0.0'   # listen on all interfaces
PORT = 5001
CHUNK_SIZE = 1024
FILE_TO_SHARE = 'Wick Is Pain (2025) WEBDL-1080p.mkv'

# Split file into chunks
with open(FILE_TO_SHARE, 'rb') as f:
    chunks = []
    while True:
        data = f.read(CHUNK_SIZE)
        if not data:
            break
        chunks.append(data)

# Hash chunks
chunk_hashes = [hashlib.sha1(c).hexdigest() for c in chunks]

# Build header
header = f"{len(chunks)}\n" + "\n".join(chunk_hashes) + "\nEND\n"

# Start server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)
print(f"[Seeder] Listening on {HOST}:{PORT}...")

conn, addr = server.accept()
print(f"[Seeder] Connected by {addr}")

# Send header
conn.sendall(header.encode())
print(f"[Seeder] Sent header: {len(chunks)} chunks, {len(chunk_hashes)} hashes")

# Send chunks
for i, c in enumerate(chunks):
    conn.sendall(c)
    print(f"[Seeder] Sent chunk {i} ({len(c)} bytes, sha1={chunk_hashes[i][:8]}...)")

print("[Seeder] File transfer complete!")
conn.close()
server.close()
