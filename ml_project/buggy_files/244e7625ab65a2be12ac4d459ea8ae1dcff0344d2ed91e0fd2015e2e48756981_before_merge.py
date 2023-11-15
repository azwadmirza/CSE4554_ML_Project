def need_deployment():
    '''
    Salt thin needs to be deployed - prep the target directory and emit the
    delimiter and exit code that signals a required deployment.
    '''
    if os.path.exists(OPTIONS.saltdir):
        shutil.rmtree(OPTIONS.saltdir)
    old_umask = os.umask(0o077)  # pylint: disable=blacklisted-function
    try:
        os.makedirs(OPTIONS.saltdir)
    finally:
        os.umask(old_umask)  # pylint: disable=blacklisted-function
    # Verify perms on saltdir
    if not is_windows():
        euid = os.geteuid()
        dstat = os.stat(OPTIONS.saltdir)
        if dstat.st_uid != euid:
            # Attack detected, try again
            need_deployment()
        if dstat.st_mode != 16832:
            # Attack detected
            need_deployment()
        # If SUDOing then also give the super user group write permissions
        sudo_gid = os.environ.get('SUDO_GID')
        if sudo_gid:
            try:
                os.chown(OPTIONS.saltdir, -1, int(sudo_gid))
                stt = os.stat(OPTIONS.saltdir)
                os.chmod(OPTIONS.saltdir, stt.st_mode | stat.S_IWGRP | stat.S_IRGRP | stat.S_IXGRP)
            except OSError:
                sys.stdout.write('\n\nUnable to set permissions on thin directory.\nIf sudo_user is set '
                        'and is not root, be certain the user is in the same group\nas the login user')
                sys.exit(1)

    # Delimiter emitted on stdout *only* to indicate shim message to master.
    sys.stdout.write("{0}\ndeploy\n".format(OPTIONS.delimiter))
    sys.exit(EX_THIN_DEPLOY)