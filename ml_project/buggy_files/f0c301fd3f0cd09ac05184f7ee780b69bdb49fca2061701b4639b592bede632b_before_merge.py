    def decorator(func):
        match = re.search('([a-z_]+)', pattern)
        if match is not None:
            mpd_commands.add(
                MpdCommand(name=match.group(), auth_required=auth_required))
        # NOTE Make pattern a bytestring to get bytestring keys in the dict
        # returned from matches.groupdict(), which is again used as a **kwargs
        # dict. This is needed to work on Python < 2.6.5.
        # See https://github.com/mopidy/mopidy/issues/302 for details.
        bytestring_pattern = pattern.encode('utf-8')
        compiled_pattern = re.compile(bytestring_pattern, flags=re.UNICODE)
        if compiled_pattern in request_handlers:
            raise ValueError('Tried to redefine handler for %s with %s' % (
                pattern, func))
        request_handlers[compiled_pattern] = func
        func.__doc__ = '    - *Pattern:* ``%s``\n\n%s' % (
            pattern, func.__doc__ or '')
        return func