  def update(self, name, val):
    self.check_exists(name)
    if name not in self.values:
      raise Exception("Unrecognized config option: {}".format(name))
    self.values[name] = val