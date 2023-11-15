def _random_string():
    id_hash = hashlib.shake_128()
    id_hash.update(uuid.uuid4().bytes)
    id_bytes = id_hash.digest(ray_constants.ID_SIZE)
    assert len(id_bytes) == ray_constants.ID_SIZE
    return id_bytes