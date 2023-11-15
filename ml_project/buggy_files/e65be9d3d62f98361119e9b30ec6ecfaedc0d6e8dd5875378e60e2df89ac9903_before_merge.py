  def parse_top_import(cls, results):
    """Splits the result of import_pattern into component strings.

    Examples:

    'from pkg import a,b,c' gives
    (('pkg', None), [('a', None), ('b', None), ('c', None)])

    'import pkg' gives
    (('pkg', None), [])

    'from pkg import a as b' gives
    (('pkg', None), [('a', 'b')])

    'import pkg as pkg2' gives
    (('pkg', 'pkg2'), [])

    Args:
      results: The values from import_pattern.

    Returns:
      A tuple of the package name and the list of imported names. Each name is a
      tuple of original name and alias.
    """

    pkg, names = results['pkg'], results.get('names', None)

    if len(pkg) == 1 and pkg[0].type == pygram.python_symbols.dotted_as_name:
      pkg_out = cls._parse_import_alias(list(pkg[0].leaves()))
    else:
      pkg_out = (''.join(map(str, pkg)).strip(), None)

    names_out = []
    if names:
      names = split_comma(names.leaves())
      for name in names:
        if len(name) == 1:
          assert name[0].type in (token.NAME, token.STAR)
          names_out.append((name[0].value, None))
        else:
          names_out.append(cls._parse_import_alias(name))

    return pkg_out, names_out