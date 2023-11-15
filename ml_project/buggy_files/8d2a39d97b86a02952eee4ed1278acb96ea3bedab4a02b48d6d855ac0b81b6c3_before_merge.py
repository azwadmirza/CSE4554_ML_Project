  def _parse_import_alias(cls, leaves):
    assert [leaf.type for leaf in leaves] == [token.NAME] * 3
    assert leaves[1].value == 'as'
    return (leaves[0].value, leaves[2].value)