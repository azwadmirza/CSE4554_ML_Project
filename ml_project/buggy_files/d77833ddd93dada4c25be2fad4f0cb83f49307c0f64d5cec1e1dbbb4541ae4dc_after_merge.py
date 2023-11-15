def prefix_from_arg(arg, shelldict):
    from ..base.context import context, locate_prefix_by_name
    'Returns a platform-native path'
    # MSYS2 converts Unix paths to Windows paths with unix seps
    # so we must check for the drive identifier too.
    if shelldict['sep'] in arg and not re.match('[a-zA-Z]:', arg):
        # strip is removing " marks, not \ - look carefully
        native_path = shelldict['path_from'](arg)
        if isdir(abspath(native_path.strip("\""))):
            prefix = abspath(native_path.strip("\""))
        else:
            raise CondaValueError('Could not find environment: %s' % native_path)
    else:
        prefix = locate_prefix_by_name(context, arg.replace('/', os.path.sep))
    return prefix