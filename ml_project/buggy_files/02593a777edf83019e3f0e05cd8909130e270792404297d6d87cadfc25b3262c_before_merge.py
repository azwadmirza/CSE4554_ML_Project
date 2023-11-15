def get_hash(data, hashtype='sha1'):

    try:  # see if hash is supported
        h = hashlib.new(hashtype)
    except:
        return None

    h.update(to_bytes(data, errors='surrogate_then_strict'))
    return h.hexdigest()