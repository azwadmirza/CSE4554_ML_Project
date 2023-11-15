    def decorator(func):
        match = re.search('([a-z_]+)', pattern)
        if match is not None:
            mpd_commands.add(
                MpdCommand(name=match.group(), auth_required=auth_required))
        compiled_pattern = re.compile(pattern, flags=re.UNICODE)
        if compiled_pattern in request_handlers:
            raise ValueError('Tried to redefine handler for %s with %s' % (
                pattern, func))
        request_handlers[compiled_pattern] = func
        func.__doc__ = '    - *Pattern:* ``%s``\n\n%s' % (
            pattern, func.__doc__ or '')
        return func