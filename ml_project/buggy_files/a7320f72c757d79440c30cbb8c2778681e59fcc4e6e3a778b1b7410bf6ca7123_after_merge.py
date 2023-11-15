  def _ReadExactly(self, n):
    ret = ""
    left = n
    while left:
      data = self.sock.recv(left)
      if not data:
        raise IOError("Expected %d bytes, got EOF after %d" % (n, len(ret)))
      ret += data
      left = n - len(ret)
    return ret