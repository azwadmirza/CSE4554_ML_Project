def setup_readline():
    """Sets up the readline module and completion suppression, if available."""
    global RL_COMPLETION_SUPPRESS_APPEND, RL_LIB, RL_CAN_RESIZE, RL_STATE, \
        readline, RL_COMPLETION_QUERY_ITEMS
    if RL_COMPLETION_SUPPRESS_APPEND is not None:
        return
    for _rlmod_name in ('gnureadline', 'readline'):
        try:
            readline = importlib.import_module(_rlmod_name)
            sys.modules['readline'] = readline
        except ImportError:
            pass
        else:
            break

    if readline is None:
        print("""Skipping setup. Because no `readline` implementation available.
            Please install a backend (`readline`, `prompt-toolkit`, etc) to use
            `xonsh` interactively.
            See https://github.com/xonsh/xonsh/issues/1170""")
        return

    import ctypes
    import ctypes.util
    uses_libedit = readline.__doc__ and 'libedit' in readline.__doc__
    readline.set_completer_delims(' \t\n')
    # Cygwin seems to hang indefinitely when querying the readline lib
    if (not ON_CYGWIN) and (not readline.__file__.endswith('.py')):
        RL_LIB = lib = ctypes.cdll.LoadLibrary(readline.__file__)
        try:
            RL_COMPLETION_SUPPRESS_APPEND = ctypes.c_int.in_dll(
                lib, 'rl_completion_suppress_append')
        except ValueError:
            # not all versions of readline have this symbol, ie Macs sometimes
            RL_COMPLETION_SUPPRESS_APPEND = None
        try:
            RL_COMPLETION_QUERY_ITEMS = ctypes.c_int.in_dll(
                lib, 'rl_completion_query_items')
        except ValueError:
            # not all versions of readline have this symbol, ie Macs sometimes
            RL_COMPLETION_QUERY_ITEMS = None
        try:
            RL_STATE = ctypes.c_int.in_dll(lib, 'rl_readline_state')
        except Exception:
            pass
        RL_CAN_RESIZE = hasattr(lib, 'rl_reset_screen_size')
    env = builtins.__xonsh_env__
    # reads in history
    readline.set_history_length(-1)
    ReadlineHistoryAdder()
    # sets up IPython-like history matching with up and down
    readline.parse_and_bind('"\e[B": history-search-forward')
    readline.parse_and_bind('"\e[A": history-search-backward')
    # Setup Shift-Tab to indent
    readline.parse_and_bind('"\e[Z": "{0}"'.format(env.get('INDENT')))

    # handle tab completion differences found in libedit readline compatibility
    # as discussed at http://stackoverflow.com/a/7116997
    if uses_libedit and ON_DARWIN:
        readline.parse_and_bind("bind ^I rl_complete")
        print('\n'.join(['', "*" * 78,
                         "libedit detected - readline will not be well behaved, including but not limited to:",
                         "   * crashes on tab completion",
                         "   * incorrect history navigation",
                         "   * corrupting long-lines",
                         "   * failure to wrap or indent lines properly",
                         "",
                         "It is highly recommended that you install gnureadline, which is installable with:",
                         "     pip install gnureadline",
                         "*" * 78]), file=sys.stderr)
    else:
        readline.parse_and_bind("tab: complete")
    # try to load custom user settings
    inputrc_name = os.environ.get('INPUTRC')
    if inputrc_name is None:
        if uses_libedit:
            inputrc_name = '.editrc'
        else:
            inputrc_name = '.inputrc'
        inputrc_name = os.path.join(os.path.expanduser('~'), inputrc_name)
    if (not ON_WINDOWS) and (not os.path.isfile(inputrc_name)):
        inputrc_name = '/etc/inputrc'
    if os.path.isfile(inputrc_name):
        try:
            readline.read_init_file(inputrc_name)
        except Exception:
            # this seems to fail with libedit
            print_exception('xonsh: could not load readline default init file.')
    # properly reset intput typed before the first prompt
    readline.set_startup_hook(carriage_return)