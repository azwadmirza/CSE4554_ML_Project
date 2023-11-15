    def setup_page(self):
        newcb = self.create_checkbox

        # --- Introspection ---
        # Basic features group
        basic_features_group = QGroupBox(_("Basic features"))
        completion_box = newcb(_("Enable code completion"), 'code_completion')
        goto_definition_box = newcb(
            _("Enable Go to definition"),
            'jedi_definition',
            tip=_("If this option is enabled, left-clicking on\n"
                  "an object name while pressing the {} key will go to\n"
                  "that object's definition (if resolved).".format(self.CTRL)))
        follow_imports_box = newcb(_("Follow imports when going to a "
                                     "definition"),
                                   'jedi_definition/follow_imports')
        show_signature_box = newcb(_("Show calltips"), 'jedi_signature_help')

        basic_features_layout = QVBoxLayout()
        basic_features_layout.addWidget(completion_box)
        basic_features_layout.addWidget(goto_definition_box)
        basic_features_layout.addWidget(follow_imports_box)
        basic_features_layout.addWidget(show_signature_box)
        basic_features_group.setLayout(basic_features_layout)

        # Advanced group
        advanced_group = QGroupBox(_("Advanced"))
        modules_textedit = self.create_textedit(
            _("Preload the following modules to make completion faster "
              "and more accurate:"),
            'preload_modules'
        )
        if is_dark_interface():
            modules_textedit.textbox.setStyleSheet(
                "border: 1px solid #32414B;"
            )

        advanced_layout = QVBoxLayout()
        advanced_layout.addWidget(modules_textedit)
        advanced_group.setLayout(advanced_layout)

        # --- Linting ---
        # Linting options
        linting_label = QLabel(_("Spyder can optionally highlight syntax "
                                 "errors and possible problems with your "
                                 "code in the editor."))
        linting_label.setOpenExternalLinks(True)
        linting_label.setWordWrap(True)
        linting_check = self.create_checkbox(
            _("Enable basic linting"),
            'pyflakes')

        linting_complexity_box = self.create_checkbox(
            _("Enable complexity linting with "
              "the Mccabe package"), 'mccabe')

        # Linting layout
        linting_layout = QVBoxLayout()
        linting_layout.addWidget(linting_label)
        linting_layout.addWidget(linting_check)
        linting_layout.addWidget(linting_complexity_box)
        linting_widget = QWidget()
        linting_widget.setLayout(linting_layout)

        # --- Code style tab ---
        # Code style label
        pep_url = (
            '<a href="https://www.python.org/dev/peps/pep-0008">PEP 8</a>')
        code_style_codes_url = _(
            "<a href='http://pycodestyle.pycqa.org/en/stable"
            "/intro.html#error-codes'>pycodestyle error codes</a>")
        code_style_label = QLabel(
            _("Spyder can use pycodestyle to analyze your code for "
              "conformance to the {} convention. You can also "
              "manually show or hide specific warnings by their "
              "{}.").format(pep_url, code_style_codes_url))
        code_style_label.setOpenExternalLinks(True)
        code_style_label.setWordWrap(True)

        # Code style checkbox
        code_style_check = self.create_checkbox(
            _("Enable code style linting"),
            'pycodestyle')

        # Code style options
        self.code_style_filenames_match = self.create_lineedit(
            _("Only check filenames matching these patterns:"),
            'pycodestyle/filename', alignment=Qt.Horizontal, word_wrap=False,
            placeholder=_("Check Python files: *.py"))
        self.code_style_exclude = self.create_lineedit(
            _("Exclude files or directories matching these patterns:"),
            'pycodestyle/exclude', alignment=Qt.Horizontal, word_wrap=False,
            placeholder=_("Exclude all test files: (?!test_).*\\.py"))
        code_style_select = self.create_lineedit(
            _("Show the following errors or warnings:").format(
                code_style_codes_url),
            'pycodestyle/select', alignment=Qt.Horizontal, word_wrap=False,
            placeholder=_("Example codes: E113, W391"))
        code_style_ignore = self.create_lineedit(
            _("Ignore the following errors or warnings:"),
            'pycodestyle/ignore', alignment=Qt.Horizontal, word_wrap=False,
            placeholder=_("Example codes: E201, E303"))
        code_style_max_line_length = self.create_spinbox(
            _("Maximum allowed line length:"), None,
            'pycodestyle/max_line_length', min_=10, max_=500, step=1,
            tip=_("Default is 79"))

        # Code style layout
        code_style_g_layout = QGridLayout()
        code_style_g_layout.addWidget(
            self.code_style_filenames_match.label, 1, 0)
        code_style_g_layout.addWidget(
            self.code_style_filenames_match.textbox, 1, 1)
        code_style_g_layout.addWidget(self.code_style_exclude.label, 2, 0)
        code_style_g_layout.addWidget(self.code_style_exclude.textbox, 2, 1)
        code_style_g_layout.addWidget(code_style_select.label, 3, 0)
        code_style_g_layout.addWidget(code_style_select.textbox, 3, 1)
        code_style_g_layout.addWidget(code_style_ignore.label, 4, 0)
        code_style_g_layout.addWidget(code_style_ignore.textbox, 4, 1)
        code_style_g_layout.addWidget(code_style_max_line_length.plabel, 5, 0)
        code_style_g_layout.addWidget(
            code_style_max_line_length.spinbox, 5, 1)

        # Set Code style options enabled/disabled
        code_style_g_widget = QWidget()
        code_style_g_widget.setLayout(code_style_g_layout)
        code_style_g_widget.setEnabled(self.get_option('pycodestyle'))
        code_style_check.toggled.connect(code_style_g_widget.setEnabled)

        # Code style layout
        code_style_layout = QVBoxLayout()
        code_style_layout.addWidget(code_style_label)
        code_style_layout.addWidget(code_style_check)
        code_style_layout.addWidget(code_style_g_widget)

        code_style_widget = QWidget()
        code_style_widget.setLayout(code_style_layout)

        # --- Docstring tab ---
        # Docstring style label
        numpy_url = (
            "<a href='https://numpydoc.readthedocs.io/en/"
            "latest/format.html'>Numpy</a>")
        pep257_url = (
            "<a href='https://www.python.org/dev/peps/pep-0257/'>PEP 257</a>")
        docstring_style_codes = _(
            "<a href='http://www.pydocstyle.org/en/stable"
            "/error_codes.html'>page</a>")
        docstring_style_label = QLabel(
            _("Here you can decide if you want to perform style analysis on "
              "your docstrings according to the {} or {} conventions. You can "
              "also decide if you want to show or ignore specific errors, "
              "according to the codes found on this {}.").format(
                  numpy_url, pep257_url, docstring_style_codes))
        docstring_style_label.setOpenExternalLinks(True)
        docstring_style_label.setWordWrap(True)

        # Docstring style checkbox
        docstring_style_check = self.create_checkbox(
            _("Enable docstring style linting"),
            'pydocstyle')

        # Docstring style options
        docstring_style_convention = self.create_combobox(
            _("Choose the convention used to lint docstrings: "),
            (("Numpy", 'numpy'),
             ("PEP 257", 'pep257'),
             ("Custom", 'custom')),
            'pydocstyle/convention')
        self.docstring_style_select = self.create_lineedit(
            _("Show the following errors:"),
            'pydocstyle/select', alignment=Qt.Horizontal, word_wrap=False,
            placeholder=_("Example codes: D413, D414"))
        self.docstring_style_ignore = self.create_lineedit(
            _("Ignore the following errors:"),
            'pydocstyle/ignore', alignment=Qt.Horizontal, word_wrap=False,
            placeholder=_("Example codes: D107, D402"))
        self.docstring_style_match = self.create_lineedit(
            _("Only check filenames matching these patterns:"),
            'pydocstyle/match', alignment=Qt.Horizontal, word_wrap=False,
            placeholder=_("Skip test files: (?!test_).*\\.py"))
        self.docstring_style_match_dir = self.create_lineedit(
            _("Only check in directories matching these patterns:"),
            'pydocstyle/match_dir', alignment=Qt.Horizontal, word_wrap=False,
            placeholder=_("Skip dot directories: [^\\.].*"))

        # Custom option handling
        docstring_style_convention.combobox.currentTextChanged.connect(
                self.setup_docstring_style_convention)
        current_convention = docstring_style_convention.combobox.currentText()
        self.setup_docstring_style_convention(current_convention)

        # Docstring style layout
        docstring_style_g_layout = QGridLayout()
        docstring_style_g_layout.addWidget(
            docstring_style_convention.label, 1, 0)
        docstring_style_g_layout.addWidget(
            docstring_style_convention.combobox, 1, 1)
        docstring_style_g_layout.addWidget(
            self.docstring_style_select.label, 2, 0)
        docstring_style_g_layout.addWidget(
            self.docstring_style_select.textbox, 2, 1)
        docstring_style_g_layout.addWidget(
            self.docstring_style_ignore.label, 3, 0)
        docstring_style_g_layout.addWidget(
            self.docstring_style_ignore.textbox, 3, 1)
        docstring_style_g_layout.addWidget(
            self.docstring_style_match.label, 4, 0)
        docstring_style_g_layout.addWidget(
            self.docstring_style_match.textbox, 4, 1)
        docstring_style_g_layout.addWidget(
            self.docstring_style_match_dir.label, 5, 0)
        docstring_style_g_layout.addWidget(
            self.docstring_style_match_dir.textbox, 5, 1)

        # Set Docstring style options enabled/disabled
        docstring_style_g_widget = QWidget()
        docstring_style_g_widget.setLayout(docstring_style_g_layout)
        docstring_style_g_widget.setEnabled(self.get_option('pydocstyle'))
        docstring_style_check.toggled.connect(
            docstring_style_g_widget.setEnabled)

        # Docstring style layout
        docstring_style_layout = QVBoxLayout()
        docstring_style_layout.addWidget(docstring_style_label)
        docstring_style_layout.addWidget(docstring_style_check)
        docstring_style_layout.addWidget(docstring_style_g_widget)

        docstring_style_widget = QWidget()
        docstring_style_widget.setLayout(docstring_style_layout)

        # --- Advanced tab ---
        # Advanced label
        advanced_label = QLabel(
            _("Please don't modify these values unless "
              "you know what you're doing!"))
        advanced_label.setWordWrap(True)
        advanced_label.setAlignment(Qt.AlignJustify)

        # Advanced options
        advanced_command_launch = self.create_lineedit(
            _("Command to launch the Python language server: "),
            'advanced/command_launch', alignment=Qt.Horizontal,
            word_wrap=False)
        advanced_host = self.create_lineedit(
            _("IP Address and port to bind the server to: "),
            'advanced/host', alignment=Qt.Horizontal,
            word_wrap=False)
        advanced_port = self.create_spinbox(
            ":", "", 'advanced/port', min_=1, max_=65535, step=1)

        # Advanced layout
        advanced_g_layout = QGridLayout()
        advanced_g_layout.addWidget(advanced_command_launch.label, 1, 0)
        advanced_g_layout.addWidget(advanced_command_launch.textbox, 1, 1)
        advanced_g_layout.addWidget(advanced_host.label, 2, 0)

        advanced_host_port_g_layout = QGridLayout()
        advanced_host_port_g_layout.addWidget(advanced_host.textbox, 1, 0)
        advanced_host_port_g_layout.addWidget(advanced_port.plabel, 1, 1)
        advanced_host_port_g_layout.addWidget(advanced_port.spinbox, 1, 2)
        advanced_g_layout.addLayout(advanced_host_port_g_layout, 2, 1)

        advanced_widget = QWidget()
        advanced_layout = QVBoxLayout()
        advanced_layout.addWidget(advanced_label)
        advanced_layout.addLayout(advanced_g_layout)
        advanced_widget.setLayout(advanced_layout)

        # --- Other servers tab ---
        # Section label
        servers_label = QLabel(
            _("Spyder uses the <a href=\"{lsp_url}\">Language Server "
              "Protocol</a> to provide code completion and linting "
              "for its Editor. Here, you can setup and configure LSP servers "
              "for languages other than Python, so Spyder can provide such "
              "features for those languages as well."
              ).format(lsp_url=LSP_URL))
        servers_label.setOpenExternalLinks(True)
        servers_label.setWordWrap(True)
        servers_label.setAlignment(Qt.AlignJustify)

        # Servers table
        table_group = QGroupBox(_('Available servers:'))
        self.table = LSPServerTable(self, text_color=ima.MAIN_FG_COLOR)
        table_layout = QVBoxLayout()
        table_layout.addWidget(self.table)
        table_group.setLayout(table_layout)

        # Buttons
        self.reset_btn = QPushButton(_("Reset to default values"))
        self.new_btn = QPushButton(_("Set up a new server"))
        self.delete_btn = QPushButton(_("Delete currently selected server"))
        self.delete_btn.setEnabled(False)

        # Slots connected to buttons
        self.new_btn.clicked.connect(self.create_new_server)
        self.reset_btn.clicked.connect(self.reset_to_default)
        self.delete_btn.clicked.connect(self.delete_server)

        # Buttons layout
        btns = [self.new_btn, self.delete_btn, self.reset_btn]
        buttons_layout = QGridLayout()
        for i, btn in enumerate(btns):
            buttons_layout.addWidget(btn, i, 1)
        buttons_layout.setColumnStretch(0, 1)
        buttons_layout.setColumnStretch(1, 2)
        buttons_layout.setColumnStretch(2, 1)

        # Combined layout
        servers_widget = QWidget()
        servers_layout = QVBoxLayout()
        servers_layout.addSpacing(-10)
        servers_layout.addWidget(servers_label)
        servers_layout.addWidget(table_group)
        servers_layout.addSpacing(10)
        servers_layout.addLayout(buttons_layout)
        servers_widget.setLayout(servers_layout)

        # --- Tabs organization ---
        tabs = QTabWidget()
        tabs.addTab(self.create_tab(basic_features_group, advanced_group),
                    _('Introspection'))
        tabs.addTab(self.create_tab(linting_widget), _('Linting'))
        tabs.addTab(self.create_tab(code_style_widget), _('Code style'))
        tabs.addTab(self.create_tab(docstring_style_widget),
                    _('Docstring style'))
        tabs.addTab(self.create_tab(advanced_widget),
                    _('Advanced'))
        tabs.addTab(self.create_tab(servers_widget), _('Other languages'))

        vlayout = QVBoxLayout()
        vlayout.addWidget(tabs)
        self.setLayout(vlayout)