import socket
import hashlib
from tqdm import tqdm

HOST = '127.0.0.1'
PORT = 5001
CHUNK_SIZE = 1024 * 1024  # must match seeder
OUTPUT_FILE = 'Wick Is Pain (2025) WEBDL-1080p-downloaded.mkv'

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
print("[Leecher] Connected")

# Read 4-byte header length
header_len_bytes = client.recv(4)
header_len = int.from_bytes(header_len_bytes, 'big')
print(f"[Leecher] Header length: {header_len} bytes")

# Read exactly header_len bytes for header
header_bytes = b""
while len(header_bytes) < header_len:
    header_bytes += client.recv(header_len - len(header_bytes))

# Parse header
lines = header_bytes.decode().splitlines()
num_chunks = int(lines[0])
chunk_hashes = lines[1:]
print(f"[Leecher] Expecting {num_chunks} chunks")

# Receive file chunks and write to disk
with open(OUTPUT_FILE, 'wb') as f:
    for i in tqdm(range(num_chunks), desc="Receiving"):
        remaining = CHUNK_SIZE
        chunk_data = b""
        while remaining > 0:
            packet = client.recv(remaining)
            if not packet:
                break
            chunk_data += packet
            remaining -= len(packet)
        # verify
        sha1 = hashlib.sha1(chunk_data).hexdigest()
        if sha1 != chunk_hashes[i]:
            print(f"[Leecher] ❌ Chunk {i} failed verification")
        f.write(chunk_data)

print(f"[Leecher] ✅ File downloaded and saved as {OUTPUT_FILE}")
client.close()
