def _exec_command( command, use_shell=None, use_tee = None, **env ):
    log.debug('_exec_command(...)')

    if use_shell is None:
        use_shell = os.name=='posix'
    if use_tee is None:
        use_tee = os.name=='posix'
    using_command = 0
    if use_shell:
        # We use shell (unless use_shell==0) so that wildcards can be
        # used.
        sh = os.environ.get('SHELL', '/bin/sh')
        if is_sequence(command):
            argv = [sh, '-c', ' '.join(list(command))]
        else:
            argv = [sh, '-c', command]
    else:
        # On NT, DOS we avoid using command.com as it's exit status is
        # not related to the exit status of a command.
        if is_sequence(command):
            argv = command[:]
        else:
            argv = shlex.split(command)

    # `spawn*p` family with path (vp, vpe, ...) are not available on windows.
    # Also prefer spawn{v,vp} in favor of spawn{ve,vpe} if no env
    # modification is actually requested as the *e* functions are not thread
    # safe on windows (https://bugs.python.org/issue6476)
    if hasattr(os, 'spawnvpe'):
        spawn_command = os.spawnvpe if env else os.spawnvp
    else:
        spawn_command = os.spawnve if env else os.spawnv
        argv[0] = find_executable(argv[0]) or argv[0]
        if not os.path.isfile(argv[0]):
            log.warn('Executable %s does not exist' % (argv[0]))
            if os.name in ['nt', 'dos']:
                # argv[0] might be internal command
                argv = [os.environ['COMSPEC'], '/C'] + argv
                using_command = 1

    _so_has_fileno = _supports_fileno(sys.stdout)
    _se_has_fileno = _supports_fileno(sys.stderr)
    so_flush = sys.stdout.flush
    se_flush = sys.stderr.flush
    if _so_has_fileno:
        so_fileno = sys.stdout.fileno()
        so_dup = os.dup(so_fileno)
    if _se_has_fileno:
        se_fileno = sys.stderr.fileno()
        se_dup = os.dup(se_fileno)

    outfile = temp_file_name()
    fout = open(outfile, 'w')
    if using_command:
        errfile = temp_file_name()
        ferr = open(errfile, 'w')

    log.debug('Running %s(%s,%r,%r,os.environ)' \
              % (spawn_command.__name__, os.P_WAIT, argv[0], argv))

    if env and sys.version_info[0] >= 3 and os.name == 'nt':
        # Pre-encode os.environ, discarding un-encodable entries,
        # to avoid it failing during encoding as part of spawn. Failure
        # is possible if the environment contains entries that are not
        # encoded using the system codepage as windows expects.
        #
        # This is not necessary on unix, where os.environ is encoded
        # using the surrogateescape error handler and decoded using
        # it as part of spawn.
        encoded_environ = {}
        for k, v in os.environ.items():
            try:
                encoded_environ[k.encode(sys.getfilesystemencoding())] = v.encode(
                    sys.getfilesystemencoding())
            except UnicodeEncodeError:
                log.debug("ignoring un-encodable env entry %s", k)
    else:
        encoded_environ = os.environ

    argv0 = argv[0]
    if not using_command:
        argv[0] = quote_arg(argv0)

    so_flush()
    se_flush()
    if _so_has_fileno:
        os.dup2(fout.fileno(), so_fileno)

    if _se_has_fileno:
        if using_command:
            #XXX: disabled for now as it does not work from cmd under win32.
            #     Tests fail on msys
            os.dup2(ferr.fileno(), se_fileno)
        else:
            os.dup2(fout.fileno(), se_fileno)
    try:
        # Use spawnv in favor of spawnve, unless necessary
        if env:
            status = spawn_command(os.P_WAIT, argv0, argv, encoded_environ)
        else:
            status = spawn_command(os.P_WAIT, argv0, argv)
    except Exception:
        errmess = str(get_exception())
        status = 999
        sys.stderr.write('%s: %s'%(errmess, argv[0]))

    so_flush()
    se_flush()
    if _so_has_fileno:
        os.dup2(so_dup, so_fileno)
        os.close(so_dup)
    if _se_has_fileno:
        os.dup2(se_dup, se_fileno)
        os.close(se_dup)

    fout.close()
    fout = open_latin1(outfile, 'r')
    text = fout.read()
    fout.close()
    os.remove(outfile)

    if using_command:
        ferr.close()
        ferr = open_latin1(errfile, 'r')
        errmess = ferr.read()
        ferr.close()
        os.remove(errfile)
        if errmess and not status:
            # Not sure how to handle the case where errmess
            # contains only warning messages and that should
            # not be treated as errors.
            #status = 998
            if text:
                text = text + '\n'
            #text = '%sCOMMAND %r FAILED: %s' %(text,command,errmess)
            text = text + errmess
            print (errmess)
    if text[-1:]=='\n':
        text = text[:-1]
    if status is None:
        status = 0

    if use_tee:
        print (text)

    return status, text