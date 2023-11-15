    def get_plugin_actions(self):
        """Return a list of actions related to plugin"""
        # ---- File menu and toolbar ----
        self.new_action = create_action(
                self,
                _("&New file..."),
                icon=ima.icon('filenew'), tip=_("New file"),
                triggered=self.new,
                context=Qt.WidgetShortcut
        )
        self.register_shortcut(self.new_action, context="Editor",
                               name="New file", add_shortcut_to_tip=True)

        self.open_last_closed_action = create_action(
                self,
                _("O&pen last closed"),
                tip=_("Open last closed"),
                triggered=self.open_last_closed
        )
        self.register_shortcut(self.open_last_closed_action, context="Editor",
                               name="Open last closed")

        self.open_action = create_action(self, _("&Open..."),
                icon=ima.icon('fileopen'), tip=_("Open file"),
                triggered=self.load,
                context=Qt.WidgetShortcut)
        self.register_shortcut(self.open_action, context="Editor",
                               name="Open file", add_shortcut_to_tip=True)

        self.revert_action = create_action(self, _("&Revert"),
                icon=ima.icon('revert'), tip=_("Revert file from disk"),
                triggered=self.revert)

        self.save_action = create_action(self, _("&Save"),
                icon=ima.icon('filesave'), tip=_("Save file"),
                triggered=self.save,
                context=Qt.WidgetShortcut)
        self.register_shortcut(self.save_action, context="Editor",
                               name="Save file", add_shortcut_to_tip=True)

        self.save_all_action = create_action(self, _("Sav&e all"),
                icon=ima.icon('save_all'), tip=_("Save all files"),
                triggered=self.save_all,
                context=Qt.WidgetShortcut)
        self.register_shortcut(self.save_all_action, context="Editor",
                               name="Save all", add_shortcut_to_tip=True)

        save_as_action = create_action(self, _("Save &as..."), None,
                ima.icon('filesaveas'), tip=_("Save current file as..."),
                triggered=self.save_as,
                context=Qt.WidgetShortcut)
        self.register_shortcut(save_as_action, "Editor", "Save As")

        save_copy_as_action = create_action(self, _("Save copy as..."), None,
                ima.icon('filesaveas'), _("Save copy of current file as..."),
                triggered=self.save_copy_as)

        print_preview_action = create_action(self, _("Print preview..."),
                tip=_("Print preview..."), triggered=self.print_preview)
        self.print_action = create_action(self, _("&Print..."),
                icon=ima.icon('print'), tip=_("Print current file..."),
                triggered=self.print_file)
        # Shortcut for close_action is defined in widgets/editor.py
        self.close_action = create_action(self, _("&Close"),
                icon=ima.icon('fileclose'), tip=_("Close current file"),
                triggered=self.close_file)

        self.close_all_action = create_action(self, _("C&lose all"),
                icon=ima.icon('filecloseall'), tip=_("Close all opened files"),
                triggered=self.close_all_files,
                context=Qt.WidgetShortcut)
        self.register_shortcut(self.close_all_action, context="Editor",
                               name="Close all")

        # ---- Find menu and toolbar ----
        _text = _("&Find text")
        find_action = create_action(self, _text, icon=ima.icon('find'),
                                    tip=_text, triggered=self.find,
                                    context=Qt.WidgetShortcut)
        self.register_shortcut(find_action, context="find_replace",
                               name="Find text", add_shortcut_to_tip=True)
        find_next_action = create_action(self, _("Find &next"),
                                         icon=ima.icon('findnext'),
                                         triggered=self.find_next,
                                         context=Qt.WidgetShortcut)
        self.register_shortcut(find_next_action, context="find_replace",
                               name="Find next")
        find_previous_action = create_action(self, _("Find &previous"),
                                             icon=ima.icon('findprevious'),
                                             triggered=self.find_previous,
                                             context=Qt.WidgetShortcut)
        self.register_shortcut(find_previous_action, context="find_replace",
                               name="Find previous")
        _text = _("&Replace text")
        replace_action = create_action(self, _text, icon=ima.icon('replace'),
                                       tip=_text, triggered=self.replace,
                                       context=Qt.WidgetShortcut)
        self.register_shortcut(replace_action, context="find_replace",
                               name="Replace text")

        # ---- Debug menu and toolbar ----
        set_clear_breakpoint_action = create_action(self,
                                    _("Set/Clear breakpoint"),
                                    icon=ima.icon('breakpoint_big'),
                                    triggered=self.set_or_clear_breakpoint,
                                    context=Qt.WidgetShortcut)
        self.register_shortcut(set_clear_breakpoint_action, context="Editor",
                               name="Breakpoint")
        set_cond_breakpoint_action = create_action(self,
                            _("Set/Edit conditional breakpoint"),
                            icon=ima.icon('breakpoint_cond_big'),
                            triggered=self.set_or_edit_conditional_breakpoint,
                            context=Qt.WidgetShortcut)
        self.register_shortcut(set_cond_breakpoint_action, context="Editor",
                               name="Conditional breakpoint")
        clear_all_breakpoints_action = create_action(self,
                                    _('Clear breakpoints in all files'),
                                    triggered=self.clear_all_breakpoints)
        self.winpdb_action = create_action(self, _("Debug with winpdb"),
                                           triggered=self.run_winpdb)
        self.winpdb_action.setEnabled(WINPDB_PATH is not None and PY2)

        # --- Debug toolbar ---
        debug_action = create_action(self, _("&Debug"),
                                     icon=ima.icon('debug'),
                                     tip=_("Debug file"),
                                     triggered=self.debug_file)
        self.register_shortcut(debug_action, context="_", name="Debug",
                               add_shortcut_to_tip=True)

        debug_next_action = create_action(self, _("Step"),
               icon=ima.icon('arrow-step-over'), tip=_("Run current line"),
               triggered=lambda: self.debug_command("next"))
        self.register_shortcut(debug_next_action, "_", "Debug Step Over",
                               add_shortcut_to_tip=True)

        debug_continue_action = create_action(self, _("Continue"),
               icon=ima.icon('arrow-continue'),
               tip=_("Continue execution until next breakpoint"),
               triggered=lambda: self.debug_command("continue"))
        self.register_shortcut(debug_continue_action, "_", "Debug Continue",
                               add_shortcut_to_tip=True)

        debug_step_action = create_action(self, _("Step Into"),
               icon=ima.icon('arrow-step-in'),
               tip=_("Step into function or method of current line"),
               triggered=lambda: self.debug_command("step"))
        self.register_shortcut(debug_step_action, "_", "Debug Step Into",
                               add_shortcut_to_tip=True)

        debug_return_action = create_action(self, _("Step Return"),
               icon=ima.icon('arrow-step-out'),
               tip=_("Run until current function or method returns"),
               triggered=lambda: self.debug_command("return"))
        self.register_shortcut(debug_return_action, "_", "Debug Step Return",
                               add_shortcut_to_tip=True)

        debug_exit_action = create_action(self, _("Stop"),
               icon=ima.icon('stop_debug'), tip=_("Stop debugging"),
               triggered=lambda: self.debug_command("exit"))
        self.register_shortcut(debug_exit_action, "_", "Debug Exit",
                               add_shortcut_to_tip=True)

        # --- Run toolbar ---
        run_action = create_action(self, _("&Run"), icon=ima.icon('run'),
                                   tip=_("Run file"),
                                   triggered=self.run_file)
        self.register_shortcut(run_action, context="_", name="Run",
                               add_shortcut_to_tip=True)

        configure_action = create_action(self, _("&Configuration per file..."),
                                         icon=ima.icon('run_settings'),
                               tip=_("Run settings"),
                               menurole=QAction.NoRole,
                               triggered=self.edit_run_configurations)
        self.register_shortcut(configure_action, context="_",
                               name="Configure", add_shortcut_to_tip=True)

        re_run_action = create_action(self, _("Re-run &last script"),
                                      icon=ima.icon('run_again'),
                            tip=_("Run again last file"),
                            triggered=self.re_run_file)
        self.register_shortcut(re_run_action, context="_",
                               name="Re-run last script",
                               add_shortcut_to_tip=True)

        run_selected_action = create_action(self, _("Run &selection or "
                                                    "current line"),
                                            icon=ima.icon('run_selection'),
                                            tip=_("Run selection or "
                                                  "current line"),
                                            triggered=self.run_selection,
                                            context=Qt.WidgetShortcut)
        self.register_shortcut(run_selected_action, context="Editor",
                               name="Run selection", add_shortcut_to_tip=True)

        run_cell_action = create_action(self,
                            _("Run cell"),
                            icon=ima.icon('run_cell'),
                            shortcut=get_shortcut('editor', 'run cell'),
                            tip=_("Run current cell \n"
                                  "[Use #%% to create cells]"),
                            triggered=self.run_cell,
                            context=Qt.WidgetShortcut)

        run_cell_advance_action = create_action(self,
                   _("Run cell and advance"),
                   icon=ima.icon('run_cell_advance'),
                   shortcut=get_shortcut('editor', 'run cell and advance'),
                   tip=_("Run current cell and go to the next one "),
                   triggered=self.run_cell_and_advance,
                   context=Qt.WidgetShortcut)

        debug_cell_action = create_action(
            self,
            _("Debug cell"),
            icon=ima.icon('debug_cell'),
            shortcut=get_shortcut('editor', 'debug cell'),
            tip=_("Debug current cell "
                  "(Alt+Shift+Enter)"),
            triggered=self.debug_cell,
            context=Qt.WidgetShortcut)

        re_run_last_cell_action = create_action(self,
                   _("Re-run last cell"),
                   tip=_("Re run last cell "),
                   triggered=self.re_run_last_cell,
                   context=Qt.WidgetShortcut)
        self.register_shortcut(re_run_last_cell_action,
                               context="Editor",
                               name='re-run last cell',
                               add_shortcut_to_tip=True)

        # --- Source code Toolbar ---
        self.todo_list_action = create_action(self,
                _("Show todo list"), icon=ima.icon('todo_list'),
                tip=_("Show comments list (TODO/FIXME/XXX/HINT/TIP/@todo/"
                      "HACK/BUG/OPTIMIZE/!!!/???)"),
                triggered=self.go_to_next_todo)
        self.todo_menu = QMenu(self)
        self.todo_menu.setStyleSheet("QMenu {menu-scrollable: 1;}")
        self.todo_list_action.setMenu(self.todo_menu)
        self.todo_menu.aboutToShow.connect(self.update_todo_menu)

        self.warning_list_action = create_action(self,
                _("Show warning/error list"), icon=ima.icon('wng_list'),
                tip=_("Show code analysis warnings/errors"),
                triggered=self.go_to_next_warning)
        self.warning_menu = QMenu(self)
        self.warning_menu.setStyleSheet("QMenu {menu-scrollable: 1;}")
        self.warning_list_action.setMenu(self.warning_menu)
        self.warning_menu.aboutToShow.connect(self.update_warning_menu)
        self.previous_warning_action = create_action(self,
                _("Previous warning/error"), icon=ima.icon('prev_wng'),
                tip=_("Go to previous code analysis warning/error"),
                triggered=self.go_to_previous_warning,
                context=Qt.WidgetShortcut)
        self.register_shortcut(self.previous_warning_action,
                               context="Editor",
                               name="Previous warning",
                               add_shortcut_to_tip=True)
        self.next_warning_action = create_action(self,
                _("Next warning/error"), icon=ima.icon('next_wng'),
                tip=_("Go to next code analysis warning/error"),
                triggered=self.go_to_next_warning,
                context=Qt.WidgetShortcut)
        self.register_shortcut(self.next_warning_action,
                               context="Editor",
                               name="Next warning",
                               add_shortcut_to_tip=True)

        self.previous_edit_cursor_action = create_action(self,
                _("Last edit location"), icon=ima.icon('last_edit_location'),
                tip=_("Go to last edit location"),
                triggered=self.go_to_last_edit_location,
                context=Qt.WidgetShortcut)
        self.register_shortcut(self.previous_edit_cursor_action,
                               context="Editor",
                               name="Last edit location",
                               add_shortcut_to_tip=True)
        self.previous_cursor_action = create_action(self,
                _("Previous cursor position"), icon=ima.icon('prev_cursor'),
                tip=_("Go to previous cursor position"),
                triggered=self.go_to_previous_cursor_position,
                context=Qt.WidgetShortcut)
        self.register_shortcut(self.previous_cursor_action,
                               context="Editor",
                               name="Previous cursor position",
                               add_shortcut_to_tip=True)
        self.next_cursor_action = create_action(self,
                _("Next cursor position"), icon=ima.icon('next_cursor'),
                tip=_("Go to next cursor position"),
                triggered=self.go_to_next_cursor_position,
                context=Qt.WidgetShortcut)
        self.register_shortcut(self.next_cursor_action,
                               context="Editor",
                               name="Next cursor position",
                               add_shortcut_to_tip=True)

        # --- Edit Toolbar ---
        self.toggle_comment_action = create_action(self,
                _("Comment")+"/"+_("Uncomment"), icon=ima.icon('comment'),
                tip=_("Comment current line or selection"),
                triggered=self.toggle_comment, context=Qt.WidgetShortcut)
        self.register_shortcut(self.toggle_comment_action, context="Editor",
                               name="Toggle comment")
        blockcomment_action = create_action(self, _("Add &block comment"),
                tip=_("Add block comment around "
                            "current line or selection"),
                triggered=self.blockcomment, context=Qt.WidgetShortcut)
        self.register_shortcut(blockcomment_action, context="Editor",
                               name="Blockcomment")
        unblockcomment_action = create_action(self,
                _("R&emove block comment"),
                tip = _("Remove comment block around "
                              "current line or selection"),
                triggered=self.unblockcomment, context=Qt.WidgetShortcut)
        self.register_shortcut(unblockcomment_action, context="Editor",
                               name="Unblockcomment")

        # ----------------------------------------------------------------------
        # The following action shortcuts are hard-coded in CodeEditor
        # keyPressEvent handler (the shortcut is here only to inform user):
        # (context=Qt.WidgetShortcut -> disable shortcut for other widgets)
        self.indent_action = create_action(self,
                _("Indent"), "Tab", icon=ima.icon('indent'),
                tip=_("Indent current line or selection"),
                triggered=self.indent, context=Qt.WidgetShortcut)
        self.unindent_action = create_action(self,
                _("Unindent"), "Shift+Tab", icon=ima.icon('unindent'),
                tip=_("Unindent current line or selection"),
                triggered=self.unindent, context=Qt.WidgetShortcut)

        self.text_uppercase_action = create_action(self,
                _("Toggle Uppercase"), icon=ima.icon('toggle_uppercase'),
                tip=_("Change to uppercase current line or selection"),
                triggered=self.text_uppercase, context=Qt.WidgetShortcut)
        self.register_shortcut(self.text_uppercase_action, context="Editor",
                               name="transform to uppercase")

        self.text_lowercase_action = create_action(self,
                _("Toggle Lowercase"), icon=ima.icon('toggle_lowercase'),
                tip=_("Change to lowercase current line or selection"),
                triggered=self.text_lowercase, context=Qt.WidgetShortcut)
        self.register_shortcut(self.text_lowercase_action, context="Editor",
                               name="transform to lowercase")
        # ----------------------------------------------------------------------

        self.win_eol_action = create_action(self,
                           _("Carriage return and line feed (Windows)"),
                           toggled=lambda checked: self.toggle_eol_chars('nt', checked))
        self.linux_eol_action = create_action(self,
                           _("Line feed (UNIX)"),
                           toggled=lambda checked: self.toggle_eol_chars('posix', checked))
        self.mac_eol_action = create_action(self,
                           _("Carriage return (Mac)"),
                           toggled=lambda checked: self.toggle_eol_chars('mac', checked))
        eol_action_group = QActionGroup(self)
        eol_actions = (self.win_eol_action, self.linux_eol_action,
                       self.mac_eol_action)
        add_actions(eol_action_group, eol_actions)
        eol_menu = QMenu(_("Convert end-of-line characters"), self)
        add_actions(eol_menu, eol_actions)

        trailingspaces_action = create_action(
            self,
            _("Remove trailing spaces"),
            triggered=self.remove_trailing_spaces)

        # Checkable actions
        showblanks_action = self._create_checkable_action(
            _("Show blank spaces"), 'blank_spaces', 'set_blanks_enabled')

        scrollpastend_action = self._create_checkable_action(
            _("Scroll past the end"), 'scroll_past_end',
            'set_scrollpastend_enabled')

        showindentguides_action = self._create_checkable_action(
            _("Show indent guides"), 'indent_guides', 'set_indent_guides')

        show_classfunc_dropdown_action = self._create_checkable_action(
            _("Show selector for classes and functions"),
            'show_class_func_dropdown', 'set_classfunc_dropdown_visible')

        show_codestyle_warnings_action = self._create_checkable_action(
            _("Show code style warnings"), 'pycodestyle',)

        show_docstring_warnings_action = self._create_checkable_action(
            _("Show docstring style warnings"), 'pydocstyle')

        underline_errors = self._create_checkable_action(
            _("Underline errors and warnings"),
            'underline_errors', 'set_underline_errors_enabled')

        self.checkable_actions = {
                'blank_spaces': showblanks_action,
                'scroll_past_end': scrollpastend_action,
                'indent_guides': showindentguides_action,
                'show_class_func_dropdown': show_classfunc_dropdown_action,
                'pycodestyle': show_codestyle_warnings_action,
                'pydocstyle': show_docstring_warnings_action,
                'underline_errors': underline_errors}

        fixindentation_action = create_action(self, _("Fix indentation"),
                      tip=_("Replace tab characters by space characters"),
                      triggered=self.fix_indentation)

        gotoline_action = create_action(self, _("Go to line..."),
                                        icon=ima.icon('gotoline'),
                                        triggered=self.go_to_line,
                                        context=Qt.WidgetShortcut)
        self.register_shortcut(gotoline_action, context="Editor",
                               name="Go to line")

        workdir_action = create_action(self,
                _("Set console working directory"),
                icon=ima.icon('DirOpenIcon'),
                tip=_("Set current console (and file explorer) working "
                            "directory to current script directory"),
                triggered=self.__set_workdir)

        self.max_recent_action = create_action(self,
            _("Maximum number of recent files..."),
            triggered=self.change_max_recent_files)
        self.clear_recent_action = create_action(self,
            _("Clear this list"), tip=_("Clear recent files list"),
            triggered=self.clear_recent_files)

        # Fixes spyder-ide/spyder#6055.
        # See: https://bugreports.qt.io/browse/QTBUG-8596
        self.tab_navigation_actions = []
        if sys.platform == 'darwin':
            self.go_to_next_file_action = create_action(
                self,
                _("Go to next file"),
                shortcut=get_shortcut('editor', 'go to previous file'),
                triggered=self.go_to_next_file,
            )
            self.go_to_previous_file_action = create_action(
                self,
                _("Go to previous file"),
                shortcut=get_shortcut('editor', 'go to next file'),
                triggered=self.go_to_previous_file,
            )
            self.register_shortcut(
                self.go_to_next_file_action,
                context="Editor",
                name="Go to next file",
            )
            self.register_shortcut(
                self.go_to_previous_file_action,
                context="Editor",
                name="Go to previous file",
            )
            self.tab_navigation_actions = [
                MENU_SEPARATOR,
                self.go_to_previous_file_action,
                self.go_to_next_file_action,
            ]

        # ---- File menu/toolbar construction ----
        self.recent_file_menu = QMenu(_("Open &recent"), self)
        self.recent_file_menu.aboutToShow.connect(self.update_recent_file_menu)

        file_menu_actions = [
            self.new_action,
            MENU_SEPARATOR,
            self.open_action,
            self.open_last_closed_action,
            self.recent_file_menu,
            MENU_SEPARATOR,
            MENU_SEPARATOR,
            self.save_action,
            self.save_all_action,
            save_as_action,
            save_copy_as_action,
            self.revert_action,
            MENU_SEPARATOR,
            print_preview_action,
            self.print_action,
            MENU_SEPARATOR,
            self.close_action,
            self.close_all_action,
            MENU_SEPARATOR,
        ]

        self.main.file_menu_actions += file_menu_actions
        file_toolbar_actions = ([self.new_action, self.open_action,
                                self.save_action, self.save_all_action] +
                                self.main.file_toolbar_actions)

        self.main.file_toolbar_actions = file_toolbar_actions

        # ---- Find menu/toolbar construction ----
        self.main.search_menu_actions = [find_action,
                                         find_next_action,
                                         find_previous_action,
                                         replace_action]
        self.main.search_toolbar_actions = [find_action,
                                            find_next_action,
                                            replace_action]

        # ---- Edit menu/toolbar construction ----
        self.edit_menu_actions = [self.toggle_comment_action,
                                  blockcomment_action, unblockcomment_action,
                                  self.indent_action, self.unindent_action,
                                  self.text_uppercase_action,
                                  self.text_lowercase_action]
        self.main.edit_menu_actions += [MENU_SEPARATOR] + self.edit_menu_actions
        edit_toolbar_actions = [self.toggle_comment_action,
                                self.unindent_action, self.indent_action]
        self.main.edit_toolbar_actions += edit_toolbar_actions

        # ---- Search menu/toolbar construction ----
        self.main.search_menu_actions += [gotoline_action]
        self.main.search_toolbar_actions += [gotoline_action]

        # ---- Run menu/toolbar construction ----
        run_menu_actions = [run_action, run_cell_action,
                            run_cell_advance_action,
                            re_run_last_cell_action, MENU_SEPARATOR,
                            run_selected_action, re_run_action,
                            configure_action, MENU_SEPARATOR]
        self.main.run_menu_actions += run_menu_actions
        run_toolbar_actions = [run_action, run_cell_action,
                               run_cell_advance_action, run_selected_action,
                               re_run_action]
        self.main.run_toolbar_actions += run_toolbar_actions

        # ---- Debug menu/toolbar construction ----
        # NOTE: 'list_breakpoints' is used by the breakpoints
        # plugin to add its "List breakpoints" action to this
        # menu
        debug_menu_actions = [
            debug_action,
            debug_cell_action,
            debug_next_action,
            debug_step_action,
            debug_return_action,
            debug_continue_action,
            debug_exit_action,
            MENU_SEPARATOR,
            set_clear_breakpoint_action,
            set_cond_breakpoint_action,
            clear_all_breakpoints_action,
            'list_breakpoints',
            MENU_SEPARATOR,
            self.winpdb_action
        ]
        self.main.debug_menu_actions += debug_menu_actions
        debug_toolbar_actions = [
            debug_action,
            debug_next_action,
            debug_step_action,
            debug_return_action,
            debug_continue_action,
            debug_exit_action
        ]
        self.main.debug_toolbar_actions += debug_toolbar_actions

        # ---- Source menu/toolbar construction ----
        source_menu_actions = [
            showblanks_action,
            scrollpastend_action,
            showindentguides_action,
            show_classfunc_dropdown_action,
            show_codestyle_warnings_action,
            show_docstring_warnings_action,
            underline_errors,
            MENU_SEPARATOR,
            self.todo_list_action,
            self.warning_list_action,
            self.previous_warning_action,
            self.next_warning_action,
            MENU_SEPARATOR,
            self.previous_edit_cursor_action,
            self.previous_cursor_action,
            self.next_cursor_action,
            MENU_SEPARATOR,
            eol_menu,
            trailingspaces_action,
            fixindentation_action
        ]
        self.main.source_menu_actions += source_menu_actions

        source_toolbar_actions = [
            self.todo_list_action,
            self.warning_list_action,
            self.previous_warning_action,
            self.next_warning_action,
            MENU_SEPARATOR,
            self.previous_edit_cursor_action,
            self.previous_cursor_action,
            self.next_cursor_action
        ]
        self.main.source_toolbar_actions += source_toolbar_actions

        # ---- Dock widget and file dependent actions ----
        self.dock_toolbar_actions = (
            file_toolbar_actions +
            [MENU_SEPARATOR] +
            source_toolbar_actions +
            [MENU_SEPARATOR] +
            run_toolbar_actions +
            [MENU_SEPARATOR] +
            debug_toolbar_actions +
            [MENU_SEPARATOR] +
            edit_toolbar_actions
        )
        self.pythonfile_dependent_actions = [
            run_action,
            configure_action,
            set_clear_breakpoint_action,
            set_cond_breakpoint_action,
            debug_action,
            debug_cell_action,
            run_selected_action,
            run_cell_action,
            run_cell_advance_action,
            re_run_last_cell_action,
            blockcomment_action,
            unblockcomment_action,
            self.winpdb_action
        ]
        self.cythonfile_compatible_actions = [run_action, configure_action]
        self.file_dependent_actions = (
            self.pythonfile_dependent_actions +
            [
                self.save_action,
                save_as_action,
                save_copy_as_action,
                print_preview_action,
                self.print_action,
                self.save_all_action,
                gotoline_action,
                workdir_action,
                self.close_action,
                self.close_all_action,
                self.toggle_comment_action,
                self.revert_action,
                self.indent_action,
                self.unindent_action
            ]
        )
        self.stack_menu_actions = [gotoline_action, workdir_action]

        return self.file_dependent_actions