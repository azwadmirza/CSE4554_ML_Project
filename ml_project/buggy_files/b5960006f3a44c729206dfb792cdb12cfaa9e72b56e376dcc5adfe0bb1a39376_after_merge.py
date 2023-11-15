  def get_type_key(self, seen=None):
    cached_changestamps, saved_key = self._cached_type_key
    if saved_key and cached_changestamps == (
        self.members.changestamp,
        self.instance_type_parameters.changestamp):
      return saved_key
    if not seen:
      seen = set()
    seen.add(self)
    key = set()
    if self.cls:
      key.add(self.cls)
    for name, var in self.instance_type_parameters.items():
      subkey = frozenset(
          value.data.get_default_type_key()  # pylint: disable=g-long-ternary
          if value.data in seen else value.data.get_type_key(seen)
          for value in var.bindings)
      key.add((name, subkey))
    if key:
      type_key = frozenset(key)
    else:
      type_key = super(SimpleAbstractValue, self).get_type_key()
    self._cached_type_key = (
        (self.members.changestamp, self.instance_type_parameters.changestamp),
        type_key)
    return type_key