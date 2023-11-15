  def __int__(self):
    assert self.is_constant

    return int(next(iter(self.values())))