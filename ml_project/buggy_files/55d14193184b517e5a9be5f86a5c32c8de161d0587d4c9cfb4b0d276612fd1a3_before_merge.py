def compile_rule(nick, pattern):
    pattern = pattern.replace('$nickname', nick)
    pattern = pattern.replace('$nick', r'{}[,:]\s+'.format(nick))
    flags = re.IGNORECASE
    if '\n' in pattern:
        flags |= re.VERBOSE
    return re.compile(pattern, flags)