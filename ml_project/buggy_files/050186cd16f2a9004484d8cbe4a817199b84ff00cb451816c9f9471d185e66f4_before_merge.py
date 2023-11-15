def ensure_type(value, value_type, origin=None):
    ''' return a configuration variable with casting
    :arg value: The value to ensure correct typing of
    :kwarg value_type: The type of the value.  This can be any of the following strings:
        :boolean: sets the value to a True or False value
        :integer: Sets the value to an integer or raises a ValueType error
        :float: Sets the value to a float or raises a ValueType error
        :list: Treats the value as a comma separated list.  Split the value
            and return it as a python list.
        :none: Sets the value to None
        :path: Expands any environment variables and tilde's in the value.
        :tmp_path: Create a unique temporary directory inside of the directory
            specified by value and return its path.
        :pathlist: Treat the value as a typical PATH string.  (On POSIX, this
            means colon separated strings.)  Split the value and then expand
            each part for environment variables and tildes.
    '''

    basedir = None
    if origin and os.path.isabs(origin) and os.path.exists(origin):
        basedir = origin

    if value_type:
        value_type = value_type.lower()

    if value_type in ('boolean', 'bool'):
        value = boolean(value, strict=False)

    elif value:
        if value_type in ('integer', 'int'):
            value = int(value)

        elif value_type == 'float':
            value = float(value)

        elif value_type == 'list':
            if isinstance(value, string_types):
                value = [x.strip() for x in value.split(',')]

        elif value_type == 'none':
            if value == "None":
                value = None

        elif value_type == 'path':
            value = resolve_path(value, basedir=basedir)

        elif value_type in ('tmp', 'temppath', 'tmppath'):
            value = resolve_path(value, basedir=basedir)
            if not os.path.exists(value):
                makedirs_safe(value, 0o700)
            prefix = 'ansible-local-%s' % os.getpid()
            value = tempfile.mkdtemp(prefix=prefix, dir=value)

        elif value_type == 'pathspec':
            if isinstance(value, string_types):
                value = value.split(os.pathsep)
            value = [resolve_path(x, basedir=basedir) for x in value]

        elif value_type == 'pathlist':
            if isinstance(value, string_types):
                value = value.split(',')
            value = [resolve_path(x, basedir=basedir) for x in value]

        # defaults to string types
        elif isinstance(value, string_types):
            value = unquote(value)

    return to_text(value, errors='surrogate_or_strict', nonstring='passthru')