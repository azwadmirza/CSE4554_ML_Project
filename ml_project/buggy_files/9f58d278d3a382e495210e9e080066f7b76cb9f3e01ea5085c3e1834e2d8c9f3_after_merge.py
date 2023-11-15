    def sanitize_dir_option_value(self, prefix: str, option: str, value: Any) -> Any:
        '''
        If the option is an installation directory option and the value is an
        absolute path, check that it resides within prefix and return the value
        as a path relative to the prefix.

        This way everyone can do f.ex, get_option('libdir') and be sure to get
        the library directory relative to prefix.

        .as_posix() keeps the posix-like file seperators Meson uses.
        '''
        try:
            value = PurePath(value)
        except TypeError:
            return value
        if option.endswith('dir') and value.is_absolute() and \
           option not in builtin_dir_noprefix_options:
            # Value must be a subdir of the prefix
            # commonpath will always return a path in the native format, so we
            # must use pathlib.PurePath to do the same conversion before
            # comparing.
            msg = ('The value of the {!r} option is {!r} which must be a '
                   'subdir of the prefix {!r}.\nNote that if you pass a '
                   'relative path, it is assumed to be a subdir of prefix.')
            # os.path.commonpath doesn't understand case-insensitive filesystems,
            # but PurePath().relative_to() does.
            try:
                value = value.relative_to(prefix)
            except ValueError:
                raise MesonException(msg.format(option, value, prefix))
            if '..' in str(value):
                raise MesonException(msg.format(option, value, prefix))
        return value.as_posix()