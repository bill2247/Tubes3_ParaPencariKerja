# Kunci rahasia untuk enkripsi.
SECRET_KEY = "kunciRahasiaTubes3StimaYangSangatPanjangDanUnik"

class LCG:
    def __init__(self, seed):
        self.modulus = 2**32
        self.multiplier = 1664525
        self.increment = 1013904223
        self.state = seed

    def next_byte(self):
        self.state = (self.multiplier * self.state + self.increment) % self.modulus
        return self.state >> 24

def _generate_seed_from_key(key_str):
    seed = 0
    for char in key_str:
        seed = (seed * 31 + ord(char)) & 0xFFFFFFFF
    return seed

def _process_data(input_bytes, key_str):
    if not input_bytes:
        return input_bytes

    seed = _generate_seed_from_key(key_str)
    lcg = LCG(seed)
    
    processed_bytes = bytearray()
    for byte in input_bytes:
        keystream_byte = lcg.next_byte()
        processed_byte = byte ^ keystream_byte
        processed_bytes.append(processed_byte)
    
    return bytes(processed_bytes)

def encrypt(plain_text):
    if not isinstance(plain_text, str):
        plain_text = str(plain_text)
    input_bytes = plain_text.encode('utf-8')
    return _process_data(input_bytes, SECRET_KEY)

def decrypt(encrypted_bytes):
    if not isinstance(encrypted_bytes, bytes):
        return encrypted_bytes

    decrypted_bytes = _process_data(encrypted_bytes, SECRET_KEY)
    
    try:
        return decrypted_bytes.decode('utf-8')
    except UnicodeDecodeError:
        return ""
