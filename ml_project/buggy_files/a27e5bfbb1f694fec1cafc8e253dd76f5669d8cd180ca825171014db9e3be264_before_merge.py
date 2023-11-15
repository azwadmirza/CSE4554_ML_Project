  def __exit__(self, exc_type, exc_value, traceback):
    self._total = time.clock() - self._start_time
    del self._start_time