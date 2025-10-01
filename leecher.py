import socket
import hashlib
from tqdm import tqdm

# ----------------- Config -----------------
HOST = '127.0.0.1'  # Seeder IP
PORT = 5001
CHUNK_SIZE = 1024 * 1024  # must match seeder
# -----------------------------------------

print(f"[Leecher] Connecting to {HOST}:{PORT}...")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
print("[Leecher] Connected!")

# Step 1: read 4-byte header length
header_len_bytes = client.recv(4)
header_len = int.from_bytes(header_len_bytes, 'big')
print(f"[Leecher] Header length: {header_len} bytes")

# Step 2: read header
header_data = b""
while len(header_data) < header_len:
    header_data += client.recv(header_len - len(header_data))

header_text = header_data.decode()
lines = header_text.splitlines()

# Extract file info
file_name = lines[0]
num_chunks = int(lines[1])
chunk_hashes = lines[2:]
print(f"[Leecher] File: {file_name}, Chunks: {num_chunks}, Hashes received: {len(chunk_hashes)}")

# Step 3: receive chunks
chunks = []
for i in range(num_chunks):
    data = b''
    while len(data) < CHUNK_SIZE:
        packet = client.recv(CHUNK_SIZE - len(data))
        if not packet:
            break
        data += packet
    chunks.append(data)
    if i % 10 == 0 or i == num_chunks - 1:
        print(f"[Leecher] Received chunk {i + 1}/{num_chunks}")

# Step 4: verify and save
output_file = f"downloaded_{file_name}"
with open(output_file, 'wb') as f:
    for i, c in enumerate(chunks):
        sha1 = hashlib.sha1(c).hexdigest()
        if sha1 != chunk_hashes[i]:
            print(f"[Leecher] ❌ Chunk {i + 1} verification failed (got {sha1[:8]}..., expected {chunk_hashes[i][:8]}...)")
        else:
            print(f"[Leecher] ✅ Chunk {i + 1} verified ({sha1[:8]}...)")
        f.write(c)

print(f"[Leecher] ✅ File downloaded and saved as {output_file}")
client.close()
