def determine_target_prefix(ctx, args=None):
    """Get the prefix to operate in.  The prefix may not yet exist.

    Args:
        ctx: the context of conda
        args: the argparse args from the command line

    Returns: the prefix
    Raises: CondaEnvironmentNotFoundError if the prefix is invalid
    """

    argparse_args = args or ctx._argparse_args
    try:
        prefix_name = argparse_args.name
    except AttributeError:
        prefix_name = None
    try:
        prefix_path = argparse_args.prefix
    except AttributeError:
        prefix_path = None

    if prefix_name is None and prefix_path is None:
        return ctx.default_prefix
    elif prefix_path is not None:
        return expand(prefix_path)
    else:
        if '/' in prefix_name:
            from ..exceptions import CondaValueError
            raise CondaValueError("'/' not allowed in environment name: %s" %
                                  prefix_name)
        if prefix_name in (ROOT_ENV_NAME, 'root'):
            return ctx.root_prefix
        else:
            from ..exceptions import EnvironmentNameNotFound
            try:
                return locate_prefix_by_name(prefix_name)
            except EnvironmentNameNotFound:
                return join(_first_writable_envs_dir(), prefix_name)