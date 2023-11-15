def kernel_config():
    """Create a config object with IPython kernel options."""
    from IPython.core.application import get_ipython_dir
    from traitlets.config.loader import Config, load_pyconfig_files
    if not IS_EXT_INTERPRETER:
        from spyder.config.main import CONF
        from spyder.utils.programs import is_module_installed
    else:
        # We add "spyder" to sys.path for external interpreters,
        # so this works!
        # See create_kernel_spec of plugins/ipythonconsole
        from config.main import CONF
        from utils.programs import is_module_installed

    # ---- IPython config ----
    try:
        profile_path = osp.join(get_ipython_dir(), 'profile_default')
        cfg = load_pyconfig_files(['ipython_config.py',
                                   'ipython_kernel_config.py'],
                                  profile_path)
    except:
        cfg = Config()

    # ---- Spyder config ----
    spy_cfg = Config()

    # Until we implement Issue 1052
    spy_cfg.InteractiveShell.xmode = 'Plain'

    # Using Jedi slow completions a lot for objects
    # with big repr's
    spy_cfg.IPCompleter.use_jedi = False

    # Run lines of code at startup
    run_lines_o = CONF.get('ipython_console', 'startup/run_lines')
    if run_lines_o:
        spy_cfg.IPKernelApp.exec_lines = [x.strip() for x in run_lines_o.split(',')]
    else:
        spy_cfg.IPKernelApp.exec_lines = []

    # Clean terminal arguments input
    clear_argv = "import sys;sys.argv = [''];del sys"
    spy_cfg.IPKernelApp.exec_lines.append(clear_argv)

    # Pylab configuration
    mpl_backend = None
    mpl_installed = is_module_installed('matplotlib')
    pylab_o = CONF.get('ipython_console', 'pylab')

    if mpl_installed and pylab_o:
        # Get matplotlib backend
        backend_o = CONF.get('ipython_console', 'pylab/backend')
        if backend_o == 1:
            if is_module_installed('PyQt5'):
                auto_backend = 'qt5'
            elif is_module_installed('PyQt4'):
                auto_backend = 'qt4'
            elif is_module_installed('_tkinter'):
                auto_backend = 'tk'
            else:
                auto_backend = 'inline'
        else:
            auto_backend = ''
        backends = {0: 'inline', 1: auto_backend, 2: 'qt5', 3: 'qt4',
                    4: 'osx', 5: 'gtk3', 6: 'gtk', 7: 'wx', 8: 'tk'}
        mpl_backend = backends[backend_o]

        # Automatically load Pylab and Numpy, or only set Matplotlib
        # backend
        autoload_pylab_o = CONF.get('ipython_console', 'pylab/autoload')
        if autoload_pylab_o:
            spy_cfg.IPKernelApp.exec_lines.append(
                                              "%pylab {0}".format(mpl_backend))
        else:
            spy_cfg.IPKernelApp.exec_lines.append(
                                         "%matplotlib {0}".format(mpl_backend))

        # Inline backend configuration
        if mpl_backend == 'inline':
            # Figure format
            format_o = CONF.get('ipython_console',
                                'pylab/inline/figure_format', 0)
            formats = {0: 'png', 1: 'svg'}
            spy_cfg.InlineBackend.figure_format = formats[format_o]

            # Resolution
            if is_module_installed('ipykernel', '<4.5'):
                dpi_option = 'savefig.dpi'
            else:
                dpi_option = 'figure.dpi'

            spy_cfg.InlineBackend.rc = {'figure.figsize': (6.0, 4.0),
                                        dpi_option: 72,
                                        'font.size': 10,
                                        'figure.subplot.bottom': .125,
                                        'figure.facecolor': 'white',
                                        'figure.edgecolor': 'white'}
            resolution_o = CONF.get('ipython_console',
                                    'pylab/inline/resolution')
            spy_cfg.InlineBackend.rc[dpi_option] = resolution_o

            # Figure size
            width_o = float(CONF.get('ipython_console', 'pylab/inline/width'))
            height_o = float(CONF.get('ipython_console', 'pylab/inline/height'))
            spy_cfg.InlineBackend.rc['figure.figsize'] = (width_o, height_o)


    # Enable Cython magic
    if is_module_installed('Cython'):
        spy_cfg.IPKernelApp.exec_lines.append('%load_ext Cython')

    # Run a file at startup
    use_file_o = CONF.get('ipython_console', 'startup/use_run_file')
    run_file_o = CONF.get('ipython_console', 'startup/run_file')
    if use_file_o and run_file_o:
        spy_cfg.IPKernelApp.file_to_run = run_file_o

    # Autocall
    autocall_o = CONF.get('ipython_console', 'autocall')
    spy_cfg.ZMQInteractiveShell.autocall = autocall_o

    # To handle the banner by ourselves in IPython 3+
    spy_cfg.ZMQInteractiveShell.banner1 = ''

    # Greedy completer
    greedy_o = CONF.get('ipython_console', 'greedy_completer')
    spy_cfg.IPCompleter.greedy = greedy_o

    # Sympy loading
    sympy_o = CONF.get('ipython_console', 'symbolic_math')
    if sympy_o and is_module_installed('sympy'):
        lines = sympy_config(mpl_backend)
        spy_cfg.IPKernelApp.exec_lines.append(lines)

    # Merge IPython and Spyder configs. Spyder prefs will have prevalence
    # over IPython ones
    cfg._merge(spy_cfg)
    return cfg