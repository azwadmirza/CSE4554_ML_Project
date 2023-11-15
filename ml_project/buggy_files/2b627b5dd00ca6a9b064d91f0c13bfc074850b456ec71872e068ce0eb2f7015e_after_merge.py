    def __init__(self, parent, language=None, cmd='', host='127.0.0.1',
                 port=2084, args='', external=False, configurations={},
                 **kwargs):
        super(LSPServerEditor, self).__init__(parent)
        self.parent = parent
        self.external = external
        bbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_ok = bbox.button(QDialogButtonBox.Ok)
        self.button_cancel = bbox.button(QDialogButtonBox.Cancel)
        self.button_ok.setEnabled(False)

        description = _('To create a new configuration, '
                        'you need to select a programming '
                        'language, along with a executable '
                        'name for the server to execute '
                        '(If the instance is local), '
                        'and the host and port. Finally, '
                        'you need to provide the '
                        'arguments that the server accepts. '
                        'The placeholders <tt>{host}</tt> and '
                        '<tt>{port}</tt> refer to the host '
                        'and the port, respectively.')
        server_settings_description = QLabel(description)
        server_settings_description.setWordWrap(True)

        lang_label = QLabel(_('Language:'))
        self.lang_cb = QComboBox(self)
        self.lang_cb.setToolTip(_('Programming language provided '
                                  'by the LSP server'))
        self.lang_cb.addItem(_('Select a language'))
        self.lang_cb.addItems(LSP_LANGUAGES)

        if language is not None:
            idx = LSP_LANGUAGES.index(language)
            self.lang_cb.setCurrentIndex(idx + 1)
            self.button_ok.setEnabled(True)

        host_label = QLabel(_('Host:'))
        self.host_input = QLineEdit(self)
        self.host_input.setToolTip(_('Name of the host that will provide '
                                     'access to the server'))
        self.host_input.setText(host)
        self.host_input.textChanged.connect(lambda x: self.validate())

        port_label = QLabel(_('Port:'))
        self.port_spinner = QSpinBox(self)
        self.port_spinner.setToolTip(_('TCP port number of the server'))
        self.port_spinner.setMinimum(1)
        self.port_spinner.setMaximum(60000)
        self.port_spinner.setValue(port)

        cmd_label = QLabel(_('Command to execute:'))
        self.cmd_input = QLineEdit(self)
        self.cmd_input.setToolTip(_('Command used to start the '
                                    'LSP server locally'))
        self.cmd_input.setText(cmd)

        if not external:
            self.cmd_input.textChanged.connect(lambda x: self.validate())

        args_label = QLabel(_('Server arguments:'))
        self.args_input = QLineEdit(self)
        self.args_input.setToolTip(_('Additional arguments required to '
                                     'start the server'))
        self.args_input.setText(args)

        conf_label = QLabel(_('LSP Server Configurations:'))
        self.conf_input = CodeEditor(None)
        self.conf_input.textChanged.connect(self.validate)
        color_scheme = CONF.get('appearance', 'selected')
        self.conf_input.setup_editor(
            language='JSON',
            color_scheme=color_scheme,
            wrap=False,
            edge_line=True,
            highlight_current_line=True,
            highlight_current_cell=True,
            occurrence_highlighting=True,
            auto_unindent=True,
            font=get_font(),
            filename='config.json')
        self.conf_input.setToolTip(_('Additional LSP server configurations '
                                     'set at runtime. JSON required'))
        conf_text = '{}'
        try:
            conf_text = json.dumps(configurations, indent=4, sort_keys=True)
        except Exception:
            pass
        self.conf_input.set_text(conf_text)
        self.json_label = QLabel(self.JSON_VALID, self)

        self.external_cb = QCheckBox(_('External server'), self)
        self.external_cb.setToolTip(_('Check if the server runs '
                                      'on a remote location'))
        self.external_cb.setChecked(external)
        self.external_cb.stateChanged.connect(self.set_local_options)

        hlayout = QHBoxLayout()
        general_vlayout = QVBoxLayout()
        general_vlayout.addWidget(server_settings_description)

        vlayout = QVBoxLayout()
        lang_layout = QVBoxLayout()
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_cb)

        # layout2 = QHBoxLayout()
        # layout2.addLayout(lang_layout)
        lang_layout.addWidget(self.external_cb)
        vlayout.addLayout(lang_layout)

        host_layout = QVBoxLayout()
        host_layout.addWidget(host_label)
        host_layout.addWidget(self.host_input)

        port_layout = QVBoxLayout()
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.port_spinner)

        conn_info_layout = QHBoxLayout()
        conn_info_layout.addLayout(host_layout)
        conn_info_layout.addLayout(port_layout)
        vlayout.addLayout(conn_info_layout)

        cmd_layout = QVBoxLayout()
        cmd_layout.addWidget(cmd_label)
        cmd_layout.addWidget(self.cmd_input)
        vlayout.addLayout(cmd_layout)

        args_layout = QVBoxLayout()
        args_layout.addWidget(args_label)
        args_layout.addWidget(self.args_input)
        vlayout.addLayout(args_layout)

        conf_layout = QVBoxLayout()
        conf_layout.addWidget(conf_label)
        conf_layout.addWidget(self.conf_input)
        conf_layout.addWidget(self.json_label)

        hlayout.addLayout(vlayout)
        hlayout.addLayout(conf_layout)
        general_vlayout.addLayout(hlayout)

        general_vlayout.addWidget(bbox)
        self.setLayout(general_vlayout)
        bbox.accepted.connect(self.accept)
        bbox.rejected.connect(self.reject)
        self.lang_cb.currentIndexChanged.connect(
            self.lang_selection_changed)
        self.form_status(False)
        if language is not None:
            self.form_status(True)
            self.validate()