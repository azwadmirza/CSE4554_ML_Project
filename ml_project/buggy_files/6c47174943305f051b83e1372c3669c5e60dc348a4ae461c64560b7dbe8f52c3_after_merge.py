    def __init__(self, parent=None):
        if PYQT5:
            SpyderPluginWidget.__init__(self, parent, main = parent)
        else:
            SpyderPluginWidget.__init__(self, parent)

        self.internal_shell = None
        self.console = None

        # Initialize plugin
        self.initialize_plugin()

        self.no_doc_string = _("No documentation available")

        self._last_console_cb = None
        self._last_editor_cb = None

        self.plain_text = PlainText(self)
        self.rich_text = RichText(self)

        color_scheme = self.get_color_scheme()
        self.set_plain_text_font(self.get_plugin_font(), color_scheme)
        self.plain_text.editor.toggle_wrap_mode(self.get_option('wrap'))

        # Add entries to read-only editor context-menu
        self.wrap_action = create_action(self, _("Wrap lines"),
                                         toggled=self.toggle_wrap_mode)
        self.wrap_action.setChecked(self.get_option('wrap'))
        self.plain_text.editor.readonly_menu.addSeparator()
        add_actions(self.plain_text.editor.readonly_menu, (self.wrap_action,))

        self.set_rich_text_font(self.get_plugin_font('rich_text'))

        self.shell = None

        # locked = disable link with Console
        self.locked = False
        self._last_texts = [None, None]
        self._last_editor_doc = None

        # Object name
        layout_edit = QHBoxLayout()
        layout_edit.setContentsMargins(0, 0, 0, 0)
        txt = _("Source")
        if sys.platform == 'darwin':
            source_label = QLabel("  " + txt)
        else:
            source_label = QLabel(txt)
        layout_edit.addWidget(source_label)
        self.source_combo = QComboBox(self)
        self.source_combo.addItems([_("Console"), _("Editor")])
        self.source_combo.currentIndexChanged.connect(self.source_changed)
        if (not programs.is_module_installed('rope') and
                not programs.is_module_installed('jedi', '>=0.8.1')):
            self.source_combo.hide()
            source_label.hide()
        layout_edit.addWidget(self.source_combo)
        layout_edit.addSpacing(10)
        layout_edit.addWidget(QLabel(_("Object")))
        self.combo = ObjectComboBox(self)
        layout_edit.addWidget(self.combo)
        self.object_edit = QLineEdit(self)
        self.object_edit.setReadOnly(True)
        layout_edit.addWidget(self.object_edit)
        self.combo.setMaxCount(self.get_option('max_history_entries'))
        self.combo.addItems( self.load_history() )
        self.combo.setItemText(0, '')
        self.combo.valid.connect(lambda valid: self.force_refresh())

        # Plain text docstring option
        self.docstring = True
        self.rich_help = self.get_option('rich_mode', True)
        self.plain_text_action = create_action(self, _("Plain Text"),
                                               toggled=self.toggle_plain_text)

        # Source code option
        self.show_source_action = create_action(self, _("Show Source"),
                                                toggled=self.toggle_show_source)

        # Rich text option
        self.rich_text_action = create_action(self, _("Rich Text"),
                                         toggled=self.toggle_rich_text)

        # Add the help actions to an exclusive QActionGroup
        help_actions = QActionGroup(self)
        help_actions.setExclusive(True)
        help_actions.addAction(self.plain_text_action)
        help_actions.addAction(self.rich_text_action)

        # Automatic import option
        self.auto_import_action = create_action(self, _("Automatic import"),
                                                toggled=self.toggle_auto_import)
        auto_import_state = self.get_option('automatic_import')
        self.auto_import_action.setChecked(auto_import_state)

        # Lock checkbox
        self.locked_button = create_toolbutton(self,
                                               triggered=self.toggle_locked)
        layout_edit.addWidget(self.locked_button)
        self._update_lock_icon()

        # Option menu
        options_button = create_toolbutton(self, text=_('Options'),
                                           icon=ima.icon('tooloptions'))
        options_button.setPopupMode(QToolButton.InstantPopup)
        menu = QMenu(self)
        add_actions(menu, [self.rich_text_action, self.plain_text_action,
                           self.show_source_action, None,
                           self.auto_import_action])
        options_button.setMenu(menu)
        layout_edit.addWidget(options_button)

        if self.rich_help:
            self.switch_to_rich_text()
        else:
            self.switch_to_plain_text()
        self.plain_text_action.setChecked(not self.rich_help)
        self.rich_text_action.setChecked(self.rich_help)
        self.source_changed()

        # Main layout
        layout = create_plugin_layout(layout_edit)
        # we have two main widgets, but only one of them is shown at a time
        layout.addWidget(self.plain_text)
        layout.addWidget(self.rich_text)
        self.setLayout(layout)

        # Add worker thread for handling rich text rendering
        self._sphinx_thread = SphinxThread(
                                  html_text_no_doc=warning(self.no_doc_string))
        self._sphinx_thread.html_ready.connect(
                                             self._on_sphinx_thread_html_ready)
        self._sphinx_thread.error_msg.connect(self._on_sphinx_thread_error_msg)

        # Handle internal and external links
        view = self.rich_text.webview
        if not WEBENGINE:
            view.page().setLinkDelegationPolicy(QWebEnginePage.DelegateAllLinks)
        view.linkClicked.connect(self.handle_link_clicks)

        self._starting_up = True