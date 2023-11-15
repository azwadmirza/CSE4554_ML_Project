def _quote_if_contains(value, pattern):
    if next(re.finditer(pattern, value), None):
        return '"{0}"'.format(re.sub(r'(\\*)"', r'\1\1\\"', value))
    return value