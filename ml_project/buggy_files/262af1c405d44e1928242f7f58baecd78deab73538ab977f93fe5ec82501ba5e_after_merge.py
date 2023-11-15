def _print_as_set(s):
    return ('{' + '{arg}'.format(arg=', '.join(
        pprint_thing(el) for el in s)) + '}')