    def __init__(self, parent=None, namespace=None, commands=[], message=None,
                 exitfunc=None, profile=False, multithreaded=False):
        SpyderPluginWidget.__init__(self, parent)
        logger.info("Initializing...")
        self.dialog_manager = DialogManager()

        # Shell
        self.shell = InternalShell(parent, namespace, commands, message,
                                   self.get_option('max_line_count'),
                                   self.get_font(), exitfunc, profile,
                                   multithreaded)
        self.shell.status.connect(lambda msg:
                                  self.sig_show_status_message.emit(msg, 0))
        self.shell.go_to_error.connect(self.go_to_error)
        self.shell.focus_changed.connect(lambda: self.focus_changed.emit())

        # Redirecting some signals:
        self.shell.redirect_stdio.connect(lambda state:
                                          self.redirect_stdio.emit(state))

        # Find/replace widget
        self.find_widget = FindReplace(self)
        self.find_widget.set_editor(self.shell)
        self.find_widget.hide()
        self.register_widget_shortcuts(self.find_widget)

        # Main layout
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignLeft)
        btn_layout.addStretch()
        btn_layout.addWidget(self.options_button, Qt.AlignRight)
        layout = create_plugin_layout(btn_layout)
        layout.addWidget(self.shell)
        layout.addWidget(self.find_widget)
        self.setLayout(layout)
        
        # Parameters
        self.shell.toggle_wrap_mode(self.get_option('wrap'))
            
        # Accepting drops
        self.setAcceptDrops(True)

        # Traceback MessageBox
        self.error_dlg = None
        self.error_traceback = ""
        self.dismiss_error = False