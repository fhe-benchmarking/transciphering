#!/usr/bin/env python3

# Copyright (c) 2025 HomomorphicEncryption.org
# All rights reserved.
#
# This software is licensed under the terms of the Apache v2 License.
# See the LICENSE.md file for details.

"""
Generate random dataset for FHE benchmark and encrypt it using AES.
"""
import numpy as np
import struct
import aes
from utils import parse_submission_arguments

def main():
    __, params, seed, __, __, __ = parse_submission_arguments('Generate dataset for FHE benchmark.')
    DATASET_PATH = params.datadir() / f"db.txt"
    AES_KEY_PATH = params.datadir() / f"aes_key.hex"
    IV_PATH = params.datadir() / f"aes_iv.hex"
    DATASET_ENC_PATH = params.datadir() / f"db.hex"

    DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)
    db_size = params.get_db_bound()

    # Set random seed if provided
    if seed is not None:
        np.random.seed(seed)
    
    # 1. Generate the random dataset
    db_array = np.random.randint(0, 65536, size=db_size, dtype=np.uint16)
    db_str = '\n'.join(str(value) for value in db_array)
    DATASET_PATH.write_text(db_str + '\n', encoding="utf-8")

    # 2. Pack dataset into bytes for AES encryption
    packer = struct.Struct('>' + 'H' * len(db_array))
    plaintext_blocks = packer.pack(*db_array)

    # 3. Generate AES key and IV
    aes_key, iv = aes.keygen(seed)
    AES_KEY_PATH.write_text(aes_key.hex())
    if params.get_size() != 0:
        IV_PATH.write_text(iv.hex())

    # 4. Encrypt dataset using aes library
    is_ctr_mode = (params.get_size() != 0)
    ciphertext_blocks = aes.encrypt(plaintext_blocks, aes_key, iv, is_ctr_mode)
    
    # 5. Save the encrypted dataset
    DATASET_ENC_PATH.write_text(bytes(ciphertext_blocks).hex())

    # 6. Calculate expected miniworkload outputs
    MAX_PATH = params.datadir() / f"max_value.txt"
    IP_PATH = params.datadir() / f"inner_product.txt"
    
    max_value = int(np.max(db_array))
    MAX_PATH.write_text(f"{max_value}\n", encoding="utf-8")

    first_half = db_array[:len(db_array)//2]
    second_half = db_array[len(db_array)//2:len(db_array)]
    inner_product = sum((int(x) * int(y)) % (2**16) for x, y in zip(first_half, second_half)) % (2**16)
    IP_PATH.write_text(f"{inner_product}\n", encoding="utf-8")

if __name__ == "__main__":
    main()