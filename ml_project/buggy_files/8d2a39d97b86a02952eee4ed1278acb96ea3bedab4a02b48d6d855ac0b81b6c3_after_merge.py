  def _parse_import_alias(cls, leaves):
    assert leaves[-2].value == 'as'
    name = ''.join(leaf.value for leaf in leaves[:-2])
    return (name, leaves[-1].value)