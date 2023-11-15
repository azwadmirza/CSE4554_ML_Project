def main(argv):  # pylint: disable=W0613
    """Main program body"""
    thin_path = os.path.join(OPTIONS.saltdir, THIN_ARCHIVE)
    if os.path.isfile(thin_path):
        if OPTIONS.checksum != get_hash(thin_path, OPTIONS.hashfunc):
            need_deployment()
        unpack_thin(thin_path)
        # Salt thin now is available to use
    else:
        if not sys.platform.startswith('win'):
            scpstat = subprocess.Popen(['/bin/sh', '-c', 'command -v scp']).wait()
            if scpstat != 0:
                sys.exit(EX_SCP_NOT_FOUND)

        if not os.path.exists(OPTIONS.saltdir):
            need_deployment()

        if not os.path.isdir(OPTIONS.saltdir):
            sys.stderr.write(
                'ERROR: salt path "{0}" exists but is'
                ' not a directory\n'.format(OPTIONS.saltdir)
            )
            sys.exit(EX_CANTCREAT)

        version_path = os.path.normpath(os.path.join(OPTIONS.saltdir, 'version'))
        if not os.path.exists(version_path) or not os.path.isfile(version_path):
            sys.stderr.write(
                'WARNING: Unable to locate current thin '
                ' version: {0}.\n'.format(version_path)
            )
            need_deployment()
        with open(version_path, 'r') as vpo:
            cur_version = vpo.readline().strip()
        if cur_version != OPTIONS.version:
            sys.stderr.write(
                'WARNING: current thin version {0}'
                ' is not up-to-date with {1}.\n'.format(
                    cur_version, OPTIONS.version
                )
            )
            need_deployment()
        # Salt thin exists and is up-to-date - fall through and use it

    salt_call_path = os.path.join(OPTIONS.saltdir, 'salt-call')
    if not os.path.isfile(salt_call_path):
        sys.stderr.write('ERROR: thin is missing "{0}"\n'.format(salt_call_path))
        need_deployment()

    with open(os.path.join(OPTIONS.saltdir, 'minion'), 'w') as config:
        config.write(OPTIONS.config + '\n')
    if OPTIONS.ext_mods:
        ext_path = os.path.join(OPTIONS.saltdir, EXT_ARCHIVE)
        if os.path.exists(ext_path):
            unpack_ext(ext_path)
        else:
            version_path = os.path.join(OPTIONS.saltdir, 'ext_version')
            if not os.path.exists(version_path) or not os.path.isfile(version_path):
                need_ext()
            with open(version_path, 'r') as vpo:
                cur_version = vpo.readline().strip()
            if cur_version != OPTIONS.ext_mods:
                need_ext()
    # Fix parameter passing issue
    if len(ARGS) == 1:
        argv_prepared = ARGS[0].split()
    else:
        argv_prepared = ARGS

    salt_argv = [
        sys.executable,
        salt_call_path,
        '--retcode-passthrough',
        '--local',
        '--metadata',
        '--out', 'json',
        '-l', 'quiet',
        '-c', OPTIONS.saltdir,
        '--',
    ] + argv_prepared

    sys.stderr.write('SALT_ARGV: {0}\n'.format(salt_argv))

    # Only emit the delimiter on *both* stdout and stderr when completely successful.
    # Yes, the flush() is necessary.
    sys.stdout.write(OPTIONS.delimiter + '\n')
    sys.stdout.flush()
    if not OPTIONS.tty:
        sys.stderr.write(OPTIONS.delimiter + '\n')
        sys.stderr.flush()
    if OPTIONS.cmd_umask is not None:
        old_umask = os.umask(OPTIONS.cmd_umask)
    if OPTIONS.tty:
        stdout, _ = subprocess.Popen(salt_argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        sys.stdout.write(stdout)
        sys.stdout.flush()
        if OPTIONS.wipe:
            shutil.rmtree(OPTIONS.saltdir)
    elif OPTIONS.wipe:
        subprocess.call(salt_argv)
        shutil.rmtree(OPTIONS.saltdir)
    else:
        subprocess.call(salt_argv)
    if OPTIONS.cmd_umask is not None:
        os.umask(old_umask)