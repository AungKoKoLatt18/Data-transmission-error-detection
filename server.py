"""Server - Intermediate node + data corruptor"""
import random
import socket
from methods import recv_all

LISTEN = ("127.0.0.1", 5000)
CLIENT2 = ("127.0.0.1", 5001)


def rand_char(exclude=()):
    while True:
        c = chr(random.randint(33, 126))
        if c != '|' and c not in exclude:
            return c


def bit_flip(text, n=1):
    t = list(text)
    for _ in range(n):
        for _ in range(100):
            i = random.randrange(len(t))
            new = chr(ord(t[i]) ^ (1 << random.randrange(7)))
            if 32 <= ord(new) <= 126 and new != '|':
                t[i] = new
                break
    return ''.join(t)


def substitution(text):
    t = list(text)
    i = random.randrange(len(t))
    t[i] = rand_char(exclude=t[i])
    return ''.join(t)


def deletion(text):
    i = random.randrange(len(text))
    return text[:i] + text[i + 1:]


def insertion(text):
    i = random.randint(1, max(1, len(text) - 1))
    return text[:i] + rand_char() + text[i:]


def swapping(text):
    pairs = [i for i in range(len(text) - 1) if text[i] != text[i + 1]]
    if not pairs:
        return substitution(text)
    i = random.choice(pairs)
    return text[:i] + text[i + 1] + text[i] + text[i + 2:]


def multi_bit_flip(text):
    return bit_flip(text, random.randint(2, 4))


def burst(text):
    n = min(len(text), random.randint(3, 8))
    start = random.randint(0, len(text) - n)
    t = list(text)
    for i in range(start, start + n):
        t[i] = rand_char(exclude=t[i])
    return ''.join(t)


INJECTORS = {
    1: ("Bit Flip", bit_flip),
    2: ("Character Substitution", substitution),
    3: ("Character Deletion", deletion),
    4: ("Random Character Insertion", insertion),
    5: ("Character Swapping", swapping),
    6: ("Multiple Bit Flips", multi_bit_flip),
    7: ("Burst Error (3-8 chars)", burst),
}

print("Error injection methods:")
for k, (name, _) in INJECTORS.items():
    print(f"  {k}. {name}")
print("  0. Random method for every packet")
print("  8. No corruption (forward unchanged)")
mode = int(input("Select: "))

srv = socket.socket()
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(LISTEN)
srv.listen()
print(f"\nServer listening on {LISTEN}... (Ctrl+C to stop)")

while True:
    conn, addr = srv.accept()
    with conn:
        packet = recv_all(conn)
    print(f"\nReceived from Client 1: {packet}")
    data, method, control = packet.rsplit("|", 2)

    if mode == 8 or not data:
        name, corrupted = "None", data
    else:
        key = random.randint(1, 7) if mode == 0 else mode
        name, func = INJECTORS[key]
        corrupted = func(data)
        for _ in range(20):          # make sure the data really changed
            if corrupted != data:
                break
            corrupted = func(data)

    out = f"{corrupted}|{method}|{control}"
    print(f"Injection: {name}\nForwarding to Client 2: {out}")
    try:
        with socket.socket() as s:
            s.connect(CLIENT2)
            s.sendall(out.encode("ascii"))
    except ConnectionRefusedError:
        print("Client 2 is not running!")
