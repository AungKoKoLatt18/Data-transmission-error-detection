"""Error detection methods shared by Client 1 and Client 2."""

METHODS = ["PARITY", "2DPARITY", "CRC16", "HAMMING", "CHECKSUM"]


def to_bits(text):
    return ''.join(f'{ord(c):08b}' for c in text)


# 1. Even parity over the whole text (total number of 1s becomes even)
def parity(text):
    return str(to_bits(text).count('1') % 2)


# 2. 2D parity: every character is one 8-bit row; row parities + column parities
def parity_2d(text):
    rows = [f'{ord(c):08b}' for c in text]
    row_par = ''.join(str(r.count('1') % 2) for r in rows)
    col_par = ''.join(str(sum(int(r[i]) for r in rows) % 2) for i in range(8))
    return f'{row_par}:{col_par}'


# 3. CRC-16/CCITT-FALSE (poly 0x1021, init 0xFFFF)
def crc16(text):
    crc = 0xFFFF
    for b in text.encode('ascii'):
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) if crc & 0x8000 else (crc << 1)
            crc &= 0xFFFF
    return f'{crc:04X}'


# 4. Hamming(7,4): every byte = two 4-bit blocks, 3 check bits per block
def _check_bits(d):
    d1, d2, d3, d4 = d
    return (d1 ^ d2 ^ d4, d1 ^ d3 ^ d4, d2 ^ d3 ^ d4)


def hamming(text):
    out = ''
    for ch in text:
        bits = f'{ord(ch):08b}'
        for half in (bits[:4], bits[4:]):
            out += ''.join(map(str, _check_bits([int(x) for x in half])))
    return out


def hamming_correct(text, sent):
    """Try to fix single-bit errors per 4-bit block. Returns corrected text or None."""
    if len(sent) != 6 * len(text):
        return None  # length changed (insertion/deletion) -> cannot correct
    bits = list(to_bits(text))
    pos_map = {3: 0, 5: 1, 6: 2, 7: 3}  # syndrome -> data bit index in block
    for i in range(len(text) * 2):
        c = _check_bits([int(x) for x in bits[i * 4:i * 4 + 4]])
        s = [int(x) for x in sent[i * 3:i * 3 + 3]]
        syndrome = (c[0] ^ s[0]) + 2 * (c[1] ^ s[1]) + 4 * (c[2] ^ s[2])
        if syndrome in pos_map:
            k = i * 4 + pos_map[syndrome]
            bits[k] = '1' if bits[k] == '0' else '0'
    bits = ''.join(bits)
    return ''.join(chr(int(bits[i:i + 8], 2)) for i in range(0, len(bits), 8))


# 5. Internet checksum (RFC 1071)
def internet_checksum(text):
    data = text.encode('ascii')
    if len(data) % 2:
        data += b'\x00'
    s = 0
    for i in range(0, len(data), 2):
        s += (data[i] << 8) + data[i + 1]
        s = (s & 0xFFFF) + (s >> 16)
    return f'{(~s) & 0xFFFF:04X}'


def compute(method, text):
    table = {"PARITY": parity, "2DPARITY": parity_2d, "CRC16": crc16,
             "HAMMING": hamming, "CHECKSUM": internet_checksum}
    return table[method](text)


def recv_all(conn):
    chunks = []
    while True:
        part = conn.recv(4096)
        if not part:
            break
        chunks.append(part)
    return b''.join(chunks).decode('ascii', errors='replace')
