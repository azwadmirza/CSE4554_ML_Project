    def __init__(self, parent, history_filename, profile=False,
                 initial_message=None, default_foreground_color=None,
                 error_foreground_color=None, traceback_foreground_color=None,
                 prompt_foreground_color=None, background_color=None):
        """
        parent : specifies the parent widget
        """
        ConsoleBaseWidget.__init__(self, parent)
        SaveHistoryMixin.__init__(self, history_filename)
        BrowseHistoryMixin.__init__(self)
                
        # Prompt position: tuple (line, index)
        self.current_prompt_pos = None
        self.new_input_line = True
        
        # History
        assert is_text_string(history_filename)
        self.history = self.load_history()
        
        # Session
        self.historylog_filename = CONF.get('main', 'historylog_filename',
                                            get_conf_path('history.log'))
        
        # Context menu
        self.menu = None
        self.setup_context_menu()

        # Simple profiling test
        self.profile = profile
        
        # Buffer to increase performance of write/flush operations
        self.__buffer = []
        if initial_message:
            self.__buffer.append(initial_message)

        self.__timestamp = 0.0
        self.__flushtimer = QTimer(self)
        self.__flushtimer.setSingleShot(True)
        self.__flushtimer.timeout.connect(self.flush)

        # Give focus to widget
        self.setFocus()

        # Cursor width
        self.setCursorWidth(CONF.get('main', 'cursor/width'))

        # Adjustments to completion_widget to use it here
        self.completion_widget.currentRowChanged.disconnect()