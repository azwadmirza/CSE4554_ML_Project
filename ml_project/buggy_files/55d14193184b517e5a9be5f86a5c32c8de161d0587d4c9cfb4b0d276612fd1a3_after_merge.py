def compile_rule(nick, pattern):
    # Not sure why this happens on reloads, but it shouldn't cause problems…
    if isinstance(pattern, _regex_type):
        return pattern

    pattern = pattern.replace('$nickname', nick)
    pattern = pattern.replace('$nick', r'{}[,:]\s+'.format(nick))
    flags = re.IGNORECASE
    if '\n' in pattern:
        flags |= re.VERBOSE
    return re.compile(pattern, flags)