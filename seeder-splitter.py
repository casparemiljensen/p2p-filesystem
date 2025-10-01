import socket
import hashlib
import os
from tqdm import tqdm

# Config
HOST = '0.0.0.0'
PORT = 5001
CHUNK_SIZE = 1024 * 1024  # 1 MB chunks
FILE_TO_SHARE = 'Wick Is Pain (2025) WEBDL-1080p.mkv'

# Get file info
file_size = os.path.getsize(FILE_TO_SHARE)
num_chunks = (file_size + CHUNK_SIZE - 1) // CHUNK_SIZE
print(f"[Seeder] File size: {file_size} bytes, {num_chunks} chunks")

# Compute hashes (for verification)
chunk_hashes = []
with open(FILE_TO_SHARE, 'rb') as f:
    for _ in tqdm(range(num_chunks), desc="Hashing"):
        chunk = f.read(CHUNK_SIZE)
        chunk_hashes.append(hashlib.sha1(chunk).hexdigest())

# Build header as text
header_text = f"{num_chunks}\n" + "\n".join(chunk_hashes)
header_bytes = header_text.encode()
header_len = len(header_bytes)
print(f"[Seeder] Header size: {header_len} bytes")

# Start server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)
print(f"[Seeder] Listening on {HOST}:{PORT}...")
conn, addr = server.accept()
print(f"[Seeder] Connected by {addr}")

# Send 4-byte header length
conn.send(header_len.to_bytes(4, 'big'))
# Send header
conn.sendall(header_bytes)
print("[Seeder] Header sent")

# Stream file chunks
with open(FILE_TO_SHARE, 'rb') as f:
    for i in tqdm(range(num_chunks), desc="Sending"):
        chunk = f.read(CHUNK_SIZE)
        conn.sendall(chunk)

print("[Seeder] ✅ File transfer complete")
conn.close()
server.close()
