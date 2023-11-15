    def __init__(self, parent, actions):
        QWidget.__init__(self, parent)

        self.setAttribute(Qt.WA_DeleteOnClose)

        self.threadmanager = ThreadManager(self)
        self.new_window = False
        self.horsplit_action = None
        self.versplit_action = None
        self.close_action = None
        self.__get_split_actions()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.menu = None
        self.fileswitcher_dlg = None
#        self.filelist_btn = None
#        self.previous_btn = None
#        self.next_btn = None
        self.tabs = None
        self.tabs_switcher = None

        self.stack_history = StackHistory(self)

        self.setup_editorstack(parent, layout)

        self.find_widget = None

        self.data = []
        fileswitcher_action = create_action(self, _("File switcher..."),
                icon=ima.icon('filelist'),
                triggered=self.open_fileswitcher_dlg)
        symbolfinder_action = create_action(self,
                _("Find symbols in file..."),
                icon=ima.icon('symbol_find'),
                triggered=self.open_symbolfinder_dlg)
        copy_to_cb_action = create_action(self, _("Copy path to clipboard"),
                icon=ima.icon('editcopy'),
                triggered=lambda:
                QApplication.clipboard().setText(self.get_current_filename()))
        close_right = create_action(self, _("Close all to the right"),
                                    triggered=self.close_all_right)
        close_all_but_this = create_action(self, _("Close all but this"),
                                           triggered=self.close_all_but_this)

        sort_tabs = create_action(self, _("Sort tabs alphabetically"),
                                  triggered=self.sort_file_tabs_alphabetically)

        if sys.platform == 'darwin':
           text=_("Show in Finder")
        else:
           text= _("Show in external file explorer")
        external_fileexp_action = create_action(self, text,
                                triggered=self.show_in_external_file_explorer)

        self.menu_actions = actions + [external_fileexp_action,
                                       None, fileswitcher_action,
                                       symbolfinder_action,
                                       copy_to_cb_action, None, close_right,
                                       close_all_but_this, sort_tabs]
        self.outlineexplorer = None
        self.help = None
        self.unregister_callback = None
        self.is_closable = False
        self.new_action = None
        self.open_action = None
        self.save_action = None
        self.revert_action = None
        self.tempfile_path = None
        self.title = _("Editor")
        self.todolist_enabled = True
        self.is_analysis_done = False
        self.linenumbers_enabled = True
        self.blanks_enabled = False
        self.scrollpastend_enabled = False
        self.edgeline_enabled = True
        self.edgeline_columns = (79,)
        self.close_parentheses_enabled = True
        self.close_quotes_enabled = True
        self.add_colons_enabled = True
        self.auto_unindent_enabled = True
        self.indent_chars = " "*4
        self.tab_stop_width_spaces = 4
        self.show_class_func_dropdown = False
        self.help_enabled = False
        self.default_font = None
        self.wrap_enabled = False
        self.tabmode_enabled = False
        self.stripmode_enabled = False
        self.intelligent_backspace_enabled = True
        self.automatic_completions_enabled = True
        self.underline_errors_enabled = False
        self.highlight_current_line_enabled = False
        self.highlight_current_cell_enabled = False
        self.occurrence_highlighting_enabled = True
        self.occurrence_highlighting_timeout=1500
        self.checkeolchars_enabled = True
        self.always_remove_trailing_spaces = False
        self.convert_eol_on_save = False
        self.convert_eol_on_save_to = 'LF'
        self.focus_to_editor = True
        self.run_cell_copy = False
        self.create_new_file_if_empty = True
        self.indent_guides = False
        ccs = 'Spyder'
        if ccs not in syntaxhighlighters.COLOR_SCHEME_NAMES:
            ccs = syntaxhighlighters.COLOR_SCHEME_NAMES[0]
        self.color_scheme = ccs
        self.__file_status_flag = False

        # Real-time code analysis
        self.analysis_timer = QTimer(self)
        self.analysis_timer.setSingleShot(True)
        self.analysis_timer.setInterval(1000)
        self.analysis_timer.timeout.connect(self.analyze_script)

        # Update filename label
        self.editor_focus_changed.connect(self.update_fname_label)

        # Accepting drops
        self.setAcceptDrops(True)

        # Local shortcuts
        self.shortcuts = self.create_shortcuts()

        #For opening last closed tabs
        self.last_closed_files = []

        # Reference to save msgbox and avoid memory to be freed.
        self.msgbox = None

        # File types and filters used by the Save As dialog
        self.edit_filetypes = None
        self.edit_filters = None

        # For testing
        self.save_dialog_on_tests = not running_under_pytest()

        # Autusave component
        self.autosave = AutosaveForStack(self)

        self.last_cell_call = None