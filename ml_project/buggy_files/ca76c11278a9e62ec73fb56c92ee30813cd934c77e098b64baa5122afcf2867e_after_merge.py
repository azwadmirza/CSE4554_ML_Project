def __encode__(to_encode, iv, key):
    # Pad
    to_encode = __pad__(to_encode)
    # Encrypt
    c = AES.new(key.encode('UTF-8'), AES.MODE_CBC, iv.encode('UTF-8'))
    to_encode = c.encrypt(to_encode.encode('UTF-8'))
    # Encode
    to_encode = base64.b64encode(to_encode)
    return to_encode.decode("UTF-8")