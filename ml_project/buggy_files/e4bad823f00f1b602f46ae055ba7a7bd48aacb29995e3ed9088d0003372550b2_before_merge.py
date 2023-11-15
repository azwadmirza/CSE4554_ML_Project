  def __getitem__(self, idx):
    if type(idx) is tuple:
      return parse_spec('(' + ','.join(map(str, idx)) + ')')
    else:
      return parse_spec(str(idx))