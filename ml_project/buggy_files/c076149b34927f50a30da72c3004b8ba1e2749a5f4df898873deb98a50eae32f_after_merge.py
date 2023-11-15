  def fileno(self):
    return self._handler.stream.fileno()