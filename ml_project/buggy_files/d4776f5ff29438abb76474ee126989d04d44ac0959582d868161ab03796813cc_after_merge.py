def start_connection(play_context, variables, task_uuid):
    '''
    Starts the persistent connection
    '''
    candidate_paths = [C.ANSIBLE_CONNECTION_PATH or os.path.dirname(sys.argv[0])]
    candidate_paths.extend(os.environ.get('PATH', '').split(os.pathsep))
    for dirname in candidate_paths:
        ansible_connection = os.path.join(dirname, 'ansible-connection')
        if os.path.isfile(ansible_connection):
            display.vvvv("Found ansible-connection at path {0}".format(ansible_connection))
            break
    else:
        raise AnsibleError("Unable to find location of 'ansible-connection'. "
                           "Please set or check the value of ANSIBLE_CONNECTION_PATH")

    env = os.environ.copy()
    env.update({
        # HACK; most of these paths may change during the controller's lifetime
        # (eg, due to late dynamic role includes, multi-playbook execution), without a way
        # to invalidate/update, ansible-connection won't always see the same plugins the controller
        # can.
        'ANSIBLE_BECOME_PLUGINS': become_loader.print_paths(),
        'ANSIBLE_CLICONF_PLUGINS': cliconf_loader.print_paths(),
        'ANSIBLE_COLLECTIONS_PATH': to_native(os.pathsep.join(AnsibleCollectionConfig.collection_paths)),
        'ANSIBLE_CONNECTION_PLUGINS': connection_loader.print_paths(),
        'ANSIBLE_HTTPAPI_PLUGINS': httpapi_loader.print_paths(),
        'ANSIBLE_NETCONF_PLUGINS': netconf_loader.print_paths(),
        'ANSIBLE_TERMINAL_PLUGINS': terminal_loader.print_paths(),
    })
    python = sys.executable
    master, slave = pty.openpty()
    p = subprocess.Popen(
        [python, ansible_connection, to_text(os.getppid()), to_text(task_uuid)],
        stdin=slave, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env
    )
    os.close(slave)

    # We need to set the pty into noncanonical mode. This ensures that we
    # can receive lines longer than 4095 characters (plus newline) without
    # truncating.
    old = termios.tcgetattr(master)
    new = termios.tcgetattr(master)
    new[3] = new[3] & ~termios.ICANON

    try:
        termios.tcsetattr(master, termios.TCSANOW, new)
        write_to_file_descriptor(master, variables)
        write_to_file_descriptor(master, play_context.serialize())

        (stdout, stderr) = p.communicate()
    finally:
        termios.tcsetattr(master, termios.TCSANOW, old)
    os.close(master)

    if p.returncode == 0:
        result = json.loads(to_text(stdout, errors='surrogate_then_replace'))
    else:
        try:
            result = json.loads(to_text(stderr, errors='surrogate_then_replace'))
        except getattr(json.decoder, 'JSONDecodeError', ValueError):
            # JSONDecodeError only available on Python 3.5+
            result = {'error': to_text(stderr, errors='surrogate_then_replace')}

    if 'messages' in result:
        for level, message in result['messages']:
            if level == 'log':
                display.display(message, log_only=True)
            elif level in ('debug', 'v', 'vv', 'vvv', 'vvvv', 'vvvvv', 'vvvvvv'):
                getattr(display, level)(message, host=play_context.remote_addr)
            else:
                if hasattr(display, level):
                    getattr(display, level)(message)
                else:
                    display.vvvv(message, host=play_context.remote_addr)

    if 'error' in result:
        if play_context.verbosity > 2:
            if result.get('exception'):
                msg = "The full traceback is:\n" + result['exception']
                display.display(msg, color=C.COLOR_ERROR)
        raise AnsibleError(result['error'])

    return result['socket_path']