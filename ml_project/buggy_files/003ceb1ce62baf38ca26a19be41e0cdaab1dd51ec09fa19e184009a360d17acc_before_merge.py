  def __exit__(self, exc_type, exc_value, traceback):
    self._calls -= 1
    if not self._calls:
      self._time += time.clock() - self._start_time
      del self._start_time