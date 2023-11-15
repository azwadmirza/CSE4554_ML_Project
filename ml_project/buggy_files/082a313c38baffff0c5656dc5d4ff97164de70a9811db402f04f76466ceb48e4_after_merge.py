def handle_envs_list(acc, output=True):
    from .. import misc

    if output:
        print("# conda environments:")
        print("#")

    def disp_env(prefix):
        fmt = '%-20s  %s  %s'
        default = '*' if prefix == context.default_prefix else ' '
        name = (ROOT_ENV_NAME if prefix == context.root_prefix else
                basename(prefix))
        if output:
            print(fmt % (name, default, prefix))

    for prefix in misc.list_prefixes():
        disp_env(prefix)
        if prefix != context.root_prefix:
            acc.append(prefix)

    if output:
        print()