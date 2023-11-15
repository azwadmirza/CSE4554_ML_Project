    def __init__(self, ipyclient, additional_options, interpreter_versions,
                 external_kernel, *args, **kw):
        # To override the Qt widget used by RichJupyterWidget
        self.custom_control = ControlWidget
        self.custom_page_control = PageControlWidget
        self.custom_edit = True
        super(ShellWidget, self).__init__(*args, **kw)

        self.ipyclient = ipyclient
        self.additional_options = additional_options
        self.interpreter_versions = interpreter_versions
        self.external_kernel = external_kernel
        self._cwd = ''

        # Keyboard shortcuts
        self.shortcuts = self.create_shortcuts()

        # Set the color of the matched parentheses here since the qtconsole
        # uses a hard-coded value that is not modified when the color scheme is
        # set in the qtconsole constructor. See spyder-ide/spyder#4806.
        self.set_bracket_matcher_color_scheme(self.syntax_style)

        self.spyder_kernel_comm = KernelComm()
        self.spyder_kernel_comm.sig_exception_occurred.connect(
            self.sig_exception_occurred)
        self.kernel_manager = None
        self.kernel_client = None
        handlers = {
            'pdb_state': self.set_pdb_state,
            'pdb_continue': self.pdb_continue,
            'get_breakpoints': self.get_spyder_breakpoints,
            'save_files': self.handle_save_files,
        }

        for request_id in handlers:
            self.spyder_kernel_comm.register_call_handler(
                request_id, handlers[request_id])

        self.spyder_kernel_comm.sig_debugging.connect(self._debugging_hook)