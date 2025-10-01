import socket
import hashlib

# Config
HOST = '127.0.0.1'  # Seeder IP
PORT = 5001
CHUNK_SIZE = 1024
OUTPUT_FILE = 'downloaded_example.mkv'

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

# Read header until "END\n"
header_data = b""
while b"END\n" not in header_data:
    header_data += client.recv(1024)

header_text = header_data.decode()
lines = header_text.strip().splitlines()

# Parse header
num_chunks = int(lines[0])
chunk_hashes = lines[1:-1]  # all except first (count) and last (END)

print(f"[Leecher] Expecting {num_chunks} chunks")
print(f"[Leecher] Received {len(chunk_hashes)} hashes")

# Receive chunks
chunks = []
for i in range(num_chunks):
    data = b''
    while len(data) < CHUNK_SIZE:
        packet = client.recv(CHUNK_SIZE - len(data))
        if not packet:
            break
        data += packet
    chunks.append(data)
    print(f"[Leecher] Received chunk {i} ({len(data)} bytes)")

# Verify and write file
with open(OUTPUT_FILE, 'wb') as f:
    for i, c in enumerate(chunks):
        sha1 = hashlib.sha1(c).hexdigest()
        if sha1 != chunk_hashes[i]:
            print(f"[Leecher] ❌ Chunk {i} failed verification (got {sha1[:8]}..., expected {chunk_hashes[i][:8]}...)")
        else:
            print(f"[Leecher] ✅ Chunk {i} verified ({sha1[:8]}...)")
        f.write(c)

print(f"[Leecher] File downloaded and saved as {OUTPUT_FILE}")
client.close()
