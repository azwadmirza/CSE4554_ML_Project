def kernel_config():
    """Create a config object with IPython kernel options"""
    from IPython.config.loader import Config, load_pyconfig_files
    from IPython.core.application import get_ipython_dir
    from spyderlib.config.main import CONF
    from spyderlib.utils.programs import is_module_installed
    
    # ---- IPython config ----
    try:
        profile_path = osp.join(get_ipython_dir(), 'profile_default')
        ip_cfg = load_pyconfig_files(['ipython_config.py',
                                      'ipython_qtconsole_config.py'],
                                      profile_path)
    except:
        ip_cfg = Config()
    
    # ---- Spyder config ----
    spy_cfg = Config()
    
    # Until we implement Issue 1052
    spy_cfg.InteractiveShell.xmode = 'Plain'
    
    # Run lines of code at startup
    run_lines_o = CONF.get('ipython_console', 'startup/run_lines')
    if run_lines_o:
        spy_cfg.IPKernelApp.exec_lines = [x.strip() for x in run_lines_o.split(',')]
    else:
        spy_cfg.IPKernelApp.exec_lines = []
    
    # Pylab configuration
    mpl_backend = None
    mpl_installed = is_module_installed('matplotlib')
    pylab_o = CONF.get('ipython_console', 'pylab')

    if mpl_installed and pylab_o:
        # Get matplotlib backend
        backend_o = CONF.get('ipython_console', 'pylab/backend', 0)
        backends = {0: 'inline', 1: 'auto', 2: 'qt', 3: 'osx', 4: 'gtk',
                    5: 'wx', 6: 'tk'}
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
        if backends[backend_o] == 'inline':
           # Figure format
           format_o = CONF.get('ipython_console',
                               'pylab/inline/figure_format', 0)
           formats = {0: 'png', 1: 'svg'}
           spy_cfg.InlineBackend.figure_format = formats[format_o]
           
           # Resolution
           spy_cfg.InlineBackend.rc = {'figure.figsize': (6.0, 4.0),
                                   'savefig.dpi': 72,
                                   'font.size': 10,
                                   'figure.subplot.bottom': .125,
                                   'figure.facecolor': 'white',
                                   'figure.edgecolor': 'white'
                                   }
           resolution_o = CONF.get('ipython_console', 
                                   'pylab/inline/resolution')
           spy_cfg.InlineBackend.rc['savefig.dpi'] = resolution_o
           
           # Figure size
           width_o = float(CONF.get('ipython_console', 'pylab/inline/width'))
           height_o = float(CONF.get('ipython_console', 'pylab/inline/height'))
           spy_cfg.InlineBackend.rc['figure.figsize'] = (width_o, height_o)
    
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
    if sympy_o:
        lines = sympy_config(mpl_backend)
        spy_cfg.IPKernelApp.exec_lines.append(lines)

    # Merge IPython and Spyder configs. Spyder prefs will have prevalence
    # over IPython ones
    ip_cfg._merge(spy_cfg)
    return ip_cfg