def run_config(repl, config_file='~/.ptpython/config.py'):
    """
    Execute REPL config file.

    :param repl: `PythonInput` instance.
    :param config_file: Path of the configuration file.
    """
    assert isinstance(repl, PythonInput)
    assert isinstance(config_file, six.text_type)

    # Expand tildes.
    config_file = os.path.expanduser(config_file)

    def enter_to_continue():
         six.moves.input('\nPress ENTER to continue...')

    # Check whether this file exists.
    if not os.path.exists(config_file):
        print('Impossible to read %r' % config_file)
        enter_to_continue()
        return

    # Run the config file in an empty namespace.
    try:
        namespace = {}

        with open(config_file, 'rb') as f:
            code = compile(f.read(), config_file, 'exec')
            six.exec_(code, namespace, namespace)

        # Now we should have a 'configure' method in this namespace. We call this
        # method with the repl as an argument.
        if 'configure' in namespace:
            namespace['configure'](repl)

    except Exception:
         traceback.print_exc()
         enter_to_continue()