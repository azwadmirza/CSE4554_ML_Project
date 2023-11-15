  def after_create_session(self, session, coord):
    _ = coord
    for p, op, value in zip(self.placeholders, self.assign_ops, six.itervalues(self.values)):
      session.run(op, {p: value})