  def after_create_session(self, session, coord):
    _ = coord
    for variable, value in self.assign_pairs:
      variable.load(value, session=session)