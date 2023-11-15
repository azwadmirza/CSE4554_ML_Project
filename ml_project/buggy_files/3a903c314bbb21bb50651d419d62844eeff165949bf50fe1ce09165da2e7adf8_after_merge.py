def _handle_sigusr1(sig, stack):
    '''
    Signal handler for SIGUSR1, only available on Unix-like systems
    '''
    # When running in the foreground, do the right  thing
    # and spit out the debug info straight to the console
    if sys.stderr.isatty():
        output = sys.stderr
        _makepretty(output, stack)
    else:
        filename = 'salt-debug-{0}.log'.format(int(time.time()))
        destfile = os.path.join(tempfile.gettempdir(), filename)
        with salt.utils.files.fopen(destfile, 'w') as output:
            _makepretty(output, stack)