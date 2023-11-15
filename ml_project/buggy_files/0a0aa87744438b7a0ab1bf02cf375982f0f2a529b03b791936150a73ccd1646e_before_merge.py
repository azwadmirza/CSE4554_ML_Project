  def __eq__(self, other):
    return super().__eq__(ensure_poly(other))