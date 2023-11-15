    def __init__(self, parent, ignore_last_opened_files=False):
        SpyderPluginWidget.__init__(self, parent)

        self.__set_eol_chars = True

        # Creating template if it doesn't already exist
        if not osp.isfile(self.TEMPLATE_PATH):
            if os.name == "nt":
                shebang = []
            else:
                shebang = ['#!/usr/bin/env python' + ('2' if PY2 else '3')]
            header = shebang + [
                '# -*- coding: utf-8 -*-',
                '"""', 'Created on %(date)s', '',
                '@author: %(username)s', '"""', '']
            encoding.write(os.linesep.join(header), self.TEMPLATE_PATH, 'utf-8')

        self.projects = None
        self.outlineexplorer = None
        self.help = None

        self.editorstacks = None
        self.editorwindows = None
        self.editorwindows_to_be_created = None

        self.file_dependent_actions = []
        self.pythonfile_dependent_actions = []
        self.dock_toolbar_actions = None
        self.edit_menu_actions = None #XXX: find another way to notify Spyder
        # (see spyder.py: 'update_edit_menu' method)
        self.search_menu_actions = None #XXX: same thing ('update_search_menu')
        self.stack_menu_actions = None
        
        # Initialize plugin
        self.initialize_plugin()
        
        # Configuration dialog size
        self.dialog_size = None
        
        statusbar = self.main.statusBar()
        self.readwrite_status = ReadWriteStatus(self, statusbar)
        self.eol_status = EOLStatus(self, statusbar)
        self.encoding_status = EncodingStatus(self, statusbar)
        self.cursorpos_status = CursorPositionStatus(self, statusbar)
        
        layout = QVBoxLayout()
        self.dock_toolbar = QToolBar(self)
        add_actions(self.dock_toolbar, self.dock_toolbar_actions)
        layout.addWidget(self.dock_toolbar)

        self.last_edit_cursor_pos = None
        self.cursor_pos_history = []
        self.cursor_pos_index = None
        self.__ignore_cursor_position = True
        
        self.editorstacks = []
        self.last_focus_editorstack = {}
        self.editorwindows = []
        self.editorwindows_to_be_created = []
        self.toolbar_list = None
        self.menu_list = None

        # Don't start IntrospectionManager when running tests because
        # it consumes a lot of memory
        if PYTEST and not os.environ.get('SPY_TEST_USE_INTROSPECTION'):
            try:
                from unittest.mock import Mock
            except ImportError:
                from mock import Mock # Python 2
            self.introspector = Mock()
        else:
            self.introspector = IntrospectionManager(
                    extra_path=self.main.get_spyder_pythonpath())

        # Setup new windows:
        self.main.all_actions_defined.connect(self.setup_other_windows)

        # Change module completions when PYTHONPATH changes
        self.main.sig_pythonpath_changed.connect(self.set_path)

        # Find widget
        self.find_widget = FindReplace(self, enable_replace=True)
        self.find_widget.hide()
        self.find_widget.visibility_changed.connect(
                                          lambda vs: self.rehighlight_cells())
        self.register_widget_shortcuts(self.find_widget)

        # Tabbed editor widget + Find/Replace widget
        editor_widgets = QWidget(self)
        editor_layout = QVBoxLayout()
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_widgets.setLayout(editor_layout)
        self.editorsplitter = EditorSplitter(self, self,
                                         self.stack_menu_actions, first=True)
        editor_layout.addWidget(self.editorsplitter)
        editor_layout.addWidget(self.find_widget)

        # Splitter: editor widgets (see above) + outline explorer
        self.splitter = QSplitter(self)
        self.splitter.setContentsMargins(0, 0, 0, 0)
        self.splitter.addWidget(editor_widgets)
        self.splitter.setStretchFactor(0, 5)
        self.splitter.setStretchFactor(1, 1)
        layout.addWidget(self.splitter)
        self.setLayout(layout)
        self.setFocusPolicy(Qt.ClickFocus)
        
        # Editor's splitter state
        state = self.get_option('splitter_state', None)
        if state is not None:
            self.splitter.restoreState( QByteArray().fromHex(
                    str(state).encode('utf-8')) )
        
        self.recent_files = self.get_option('recent_files', [])
        self.untitled_num = 0

        # Parameters of last file execution:
        self.__last_ic_exec = None # internal console
        self.__last_ec_exec = None # external console

        # File types and filters used by the Open dialog
        self.edit_filetypes = None
        self.edit_filters = None

        self.__ignore_cursor_position = False
        current_editor = self.get_current_editor()
        if current_editor is not None:
            filename = self.get_current_filename()
            position = current_editor.get_position('cursor')
            self.add_cursor_position_to_history(filename, position)
        self.update_cursorpos_actions()
        self.set_path()