import socket
import hashlib
import os
import threading
from tqdm import tqdm

# ----------------- Config -----------------
HOST = '0.0.0.0'
PORT = 5001
CHUNK_SIZE = 1024 * 1024  # 1 MB
FILE_TO_SHARE = 'large.bin'
# -----------------------------------------

# Extract filename
file_name = os.path.basename(FILE_TO_SHARE)

# File info
file_size = os.path.getsize(FILE_TO_SHARE)
num_chunks = (file_size + CHUNK_SIZE - 1) // CHUNK_SIZE
print(f"[Seeder] File size: {file_size} bytes, {num_chunks} chunks")

# Precompute chunk hashes
chunk_hashes = []
with open(FILE_TO_SHARE, 'rb') as f:
    for _ in tqdm(range(num_chunks), desc="Hashing"):
        chunk = f.read(CHUNK_SIZE)
        chunk_hashes.append(hashlib.sha1(chunk).hexdigest())

# Build header
header_text = f"{file_name}\n{num_chunks}\n" + "\n".join(chunk_hashes)
header_bytes = header_text.encode()
header_len = len(header_bytes)
print(f"[Seeder] Header size: {header_len} bytes")

# Function to handle each connected peer
def handle_peer(conn, addr):
    try:
        print(f"[Seeder] Starting transfer to {addr}")
        # Send 4-byte header length + header
        conn.send(header_len.to_bytes(4, 'big'))
        conn.sendall(header_bytes)

        # Stream file
        with open(FILE_TO_SHARE, 'rb') as f:
            for i in range(num_chunks):
                chunk = f.read(CHUNK_SIZE)
                conn.sendall(chunk)
                if i % 10 == 0 or i == num_chunks - 1:
                    print(f"[Seeder] Sent chunk {i + 1}/{num_chunks} to {addr}")
        print(f"[Seeder] Finished transfer to {addr}")
    except Exception as e:
        print(f"[Seeder] Error with {addr}: {e}")
    finally:
        conn.close()

# Start server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(5)
print(f"[Seeder] Listening on {HOST}:{PORT}...")

# Accept connections
while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_peer, args=(conn, addr), daemon=True).start()