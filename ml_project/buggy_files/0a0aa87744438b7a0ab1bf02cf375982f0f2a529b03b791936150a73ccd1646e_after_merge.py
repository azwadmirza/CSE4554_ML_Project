  def __eq__(self, other):
    return super().__eq__(_ensure_poly(other))