  def __getitem__(self, idx):
    return parse_spec(('(' + ','.join(map(str, idx)) + ')')
                             if type(idx) is tuple else str(idx))