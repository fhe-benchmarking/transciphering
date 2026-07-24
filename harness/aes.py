import pyaes
import hashlib

def keygen(seed):
    """Generates 16-byte AES key and 16-byte IV from a seed."""
    aes_key = hashlib.sha256(str(seed).encode()).digest()[:16]
    iv = hashlib.sha256(b"iv" + str(seed).encode()).digest()[:16]
    return aes_key, iv

def encrypt(plaintext_blocks, aes_key, iv, is_ctr_mode=False):
    """Encrypts plaintext bytes using AES. is_ctr_mode=False uses ECB, True uses CTR."""
    if not is_ctr_mode:
        aes = pyaes.AES(aes_key)
        return aes.encrypt(plaintext_blocks)
    else:
        aes = pyaes.AESModeOfOperationCTR(aes_key, counter=pyaes.Counter(int.from_bytes(iv, byteorder='big')))
        return aes.encrypt(plaintext_blocks)

def decrypt(ciphertext_blocks, aes_key, iv, is_ctr_mode=False):
    """Decrypts ciphertext bytes using AES. is_ctr_mode=False uses ECB, True uses CTR."""
    if not is_ctr_mode:
        aes = pyaes.AES(aes_key)
        return aes.decrypt(ciphertext_blocks)
    else:
        aes = pyaes.AESModeOfOperationCTR(aes_key, counter=pyaes.Counter(int.from_bytes(iv, byteorder='big')))
        return aes.decrypt(ciphertext_blocks)
