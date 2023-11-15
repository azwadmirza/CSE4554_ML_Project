def main():
    from conda.config import root_env_name, root_dir, changeps1
    import conda.install
    if '-h' in sys.argv or '--help' in sys.argv:
        # all execution paths sys.exit at end.
        help(sys.argv[1], sys.argv[2])

    shell = sys.argv[2]
    shelldict = shells[shell]
    if sys.argv[1] == '..activate':
        path = get_path(shelldict)
        if len(sys.argv) == 3 or sys.argv[3].lower() == root_env_name.lower():
            binpath = binpath_from_arg(root_env_name, shelldict=shelldict)
            rootpath = None
        elif len(sys.argv) == 4:
            binpath = binpath_from_arg(sys.argv[3], shelldict=shelldict)
            rootpath = binpath_from_arg(root_env_name, shelldict=shelldict)
        else:
            sys.exit("Error: did not expect more than one argument")
        pathlist_str = pathlist_to_str(binpath)
        sys.stderr.write("prepending %s to PATH\n" % shelldict['path_to'](pathlist_str))

        # Clear the root path if it is present
        if rootpath:
            path = path.replace(shelldict['pathsep'].join(rootpath), "")

        # prepend our new entries onto the existing path and make sure that the separator is native
        path = shelldict['pathsep'].join(binpath + [path, ])

    # deactivation is handled completely in shell scripts - it restores backups of env variables.
    #    It is done in shell scripts because they handle state much better than we can here.

    elif sys.argv[1] == '..checkenv':
        if len(sys.argv) < 4:
            sys.argv.append(root_env_name)
        if len(sys.argv) > 4:
            sys.exit("Error: did not expect more than one argument.")
        if sys.argv[3].lower() == root_env_name.lower():
            # no need to check root env and try to install a symlink there
            sys.exit(0)

        # this should throw an error and exit if the env or path can't be found.
        try:
            prefix = prefix_from_arg(sys.argv[3], shelldict=shelldict)
        except ValueError as e:
            sys.exit(getattr(e, 'message', e))

        # Make sure an env always has the conda symlink
        try:
            conda.install.symlink_conda(prefix, root_dir, shell)
        except (IOError, OSError) as e:
            if e.errno == errno.EPERM or e.errno == errno.EACCES:
                msg = ("Cannot activate environment {0}, not have write access to conda symlink"
                       .format(sys.argv[2]))
                sys.exit(msg)
            raise
        sys.exit(0)

    elif sys.argv[1] == '..setps1':
        # path is a bit of a misnomer here.  It is the prompt setting.  However, it is returned
        #    below by printing.  That is why it is named "path"
        # DO NOT use os.getenv for this.  One Windows especially, it shows cmd.exe settings
        #    for bash shells.  This method uses the shell directly.
        path = os.getenv(shelldict['promptvar'], '')
        # failsafes
        if not path:
            if shelldict['exe'] == 'cmd.exe':
                path = '$P$G'
        # strip off previous prefix, if any:
        path = re.sub(".*\(\(.*\)\)\ ", "", path, count=1)
        env_path = sys.argv[3]
        if changeps1 and env_path:
            path = "(({0})) {1}".format(os.path.split(env_path)[-1], path)

    else:
        # This means there is a bug in main.py
        raise ValueError("unexpected command")

    # This print is actually what sets the PATH or PROMPT variable.  The shell
    # script gets this value, and finishes the job.
    print(path)