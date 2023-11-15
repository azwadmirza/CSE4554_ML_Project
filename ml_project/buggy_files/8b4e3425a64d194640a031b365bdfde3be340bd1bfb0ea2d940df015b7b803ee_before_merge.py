  def iter_chunks(cls, sock, return_bytes=False):
    """Generates chunks from a connected socket until an Exit chunk is sent."""
    while 1:
      chunk_type, payload = cls.read_chunk(sock, return_bytes)
      yield chunk_type, payload
      if chunk_type == ChunkType.EXIT:
        break