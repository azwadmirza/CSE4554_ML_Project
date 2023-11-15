  def __int__(self):
    assert self.is_constant
    return op.index(next(iter(self.values())))