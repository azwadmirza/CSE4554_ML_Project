def encrypt(data, encryption_version=0, _decrypt=False):
    # Version 0: Plain text
    if encryption_version == 0:
        return data
    else:
        # Simple XOR encryption, Base64 encoded
        # Version 1: unique_key1; Version 2: app.ENCRYPTION_SECRET
        key = unique_key1 if encryption_version == 1 else app.ENCRYPTION_SECRET
        if _decrypt:
            data = ensure_text(base64.decodestring(ensure_binary(data)))
            return ''.join(chr(ord(x) ^ ord(y)) for (x, y) in zip(data, cycle(key)))
        else:
            data = ''.join(chr(ord(x) ^ ord(y)) for (x, y) in zip(data, cycle(key)))
            return ensure_text(base64.encodestring(ensure_binary(data))).strip()