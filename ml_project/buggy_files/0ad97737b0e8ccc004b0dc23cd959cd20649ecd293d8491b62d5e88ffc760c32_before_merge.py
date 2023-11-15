def process_pos_args(args, via_ipc=False, cwd=None, target_arg=None):
    """Process positional commandline args.

    URLs to open have no prefix, commands to execute begin with a colon.

    Args:
        args: A list of arguments to process.
        via_ipc: Whether the arguments were transmitted over IPC.
        cwd: The cwd to use for fuzzy_url.
        target_arg: Command line argument received by a running instance via
                    ipc. If the --target argument was not specified, target_arg
                    will be an empty string.
    """
    new_window_target = ('private-window' if target_arg == 'private-window'
                         else 'window')
    command_target = config.val.new_instance_open_target
    if command_target in {'window', 'private-window'}:
        command_target = 'tab-silent'

    win_id: Optional[int] = None

    if via_ipc and not args:
        win_id = mainwindow.get_window(via_ipc=via_ipc,
                                       target=new_window_target)
        _open_startpage(win_id)
        return

    for cmd in args:
        if cmd.startswith(':'):
            if win_id is None:
                win_id = mainwindow.get_window(via_ipc=via_ipc,
                                               target=command_target)
            log.init.debug("Startup cmd {!r}".format(cmd))
            commandrunner = runners.CommandRunner(win_id)
            commandrunner.run_safely(cmd[1:])
        elif not cmd:
            log.init.debug("Empty argument")
            win_id = mainwindow.get_window(via_ipc=via_ipc,
                                           target=new_window_target)
        else:
            if via_ipc and target_arg and target_arg != 'auto':
                open_target = target_arg
            else:
                open_target = None
            if not cwd:  # could also be an empty string due to the PyQt signal
                cwd = None
            try:
                url = urlutils.fuzzy_url(cmd, cwd, relative=True)
            except urlutils.InvalidUrlError as e:
                message.error("Error in startup argument '{}': {}".format(
                    cmd, e))
            else:
                win_id = open_url(url, target=open_target, via_ipc=via_ipc)