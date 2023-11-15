    def add_history(self, filename):
        """
        Add new history tab
        Slot for add_history signal emitted by shell instance
        """
        filename = encoding.to_unicode_from_fs(filename)
        if filename in self.filenames:
            return
        editor = codeeditor.CodeEditor(self)
        if osp.splitext(filename)[1] == '.py':
            language = 'py'
        else:
            language = 'bat'
        editor.setup_editor(linenumbers=False, language=language,
                            scrollflagarea=False)
        editor.focus_changed.connect(lambda: self.focus_changed.emit())
        editor.setReadOnly(True)
        color_scheme = self.get_color_scheme()
        editor.set_font( self.get_plugin_font(), color_scheme )
        editor.toggle_wrap_mode( self.get_option('wrap') )

        text, _ = encoding.read(filename)
        text = normalize_eols(text)
        linebreaks = [m.start() for m in re.finditer('\n', text)]
        maxNline = self.get_option('max_entries')
        if len(linebreaks) > maxNline:
            text = text[linebreaks[-maxNline - 1] + 1:]
            encoding.write(text, filename)
        editor.set_text(text)
        editor.set_cursor_position('eof')
        
        self.editors.append(editor)
        self.filenames.append(filename)
        index = self.tabwidget.addTab(editor, osp.basename(filename))
        self.find_widget.set_editor(editor)
        self.tabwidget.setTabToolTip(index, filename)
        self.tabwidget.setCurrentIndex(index)