import binascii

import base58


def tron_base58_to_hex(base58_address):
    data = base58.b58decode(base58_address)

    hex_address = binascii.hexlify(data[1:-4]).decode('utf-8')

    return hex_address
