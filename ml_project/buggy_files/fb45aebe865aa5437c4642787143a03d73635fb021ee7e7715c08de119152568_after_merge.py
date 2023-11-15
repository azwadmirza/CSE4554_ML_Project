  def full_lower(self):
    if self.is_pure():
      return core.full_lower(self.val)
    else:
      return self