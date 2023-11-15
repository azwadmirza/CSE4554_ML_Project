  def __eq__(self, other):
    return (type(self) is type(other) and self.dtype == other.dtype
            and self.shape == other.shape and self.weak_type == other.weak_type
            and np.all(self.val == other.val))