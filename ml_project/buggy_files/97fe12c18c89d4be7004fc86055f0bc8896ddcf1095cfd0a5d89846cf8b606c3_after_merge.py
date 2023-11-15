    def __init__(self, parent=None, namespace=None, commands=[], message=None,
                 max_line_count=300, font=None, exitfunc=None, profile=False,
                 multithreaded=True):
        PythonShellWidget.__init__(self, parent,
                                   get_conf_path('history_internal.py'),
                                   profile=profile)

        self.multithreaded = multithreaded
        self.setMaximumBlockCount(max_line_count)

        if font is not None:
            self.set_font(font)

        # Allow raw_input support:
        self.input_loop = None
        self.input_mode = False
        
        # KeyboardInterrupt support
        self.interrupted = False # used only for not-multithreaded mode
        self.sig_keyboard_interrupt.connect(self.keyboard_interrupt)
        
        # Code completion / calltips
        getcfg = lambda option: CONF.get('internal_console', option)

        # keyboard events management
        self.eventqueue = []

        # Init interpreter
        self.exitfunc = exitfunc
        self.commands = commands
        self.message = message
        self.interpreter = None
        self.start_interpreter(namespace)
        
        # Clear status bar
        self.status.emit('')
        
        # Embedded shell -- requires the monitor (which installs the
        # 'open_in_spyder' function in builtins)
        if hasattr(builtins, 'open_in_spyder'):
            self.go_to_error.connect(self.open_with_external_spyder)