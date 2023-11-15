    def __init__(self, parent=None):
        TextEditBaseWidget.__init__(self, parent)

        self.setFocusPolicy(Qt.StrongFocus)

        # Caret (text cursor)
        self.setCursorWidth( CONF.get('main', 'cursor/width') )

        self.text_helper = TextHelper(self)

        self._panels = PanelsManager(self)

        # Mouse moving timer / Hover hints handling
        # See: mouseMoveEvent
        self.tooltip_widget.sig_help_requested.connect(
            self.show_object_info)
        self.tooltip_widget.sig_completion_help_requested.connect(
            self.show_completion_object_info)
        self._last_point = None
        self._last_hover_word = None
        self._last_hover_cursor = None
        self._timer_mouse_moving = QTimer(self)
        self._timer_mouse_moving.setInterval(350)
        self._timer_mouse_moving.setSingleShot(True)
        self._timer_mouse_moving.timeout.connect(self._handle_hover)

        # Typing keys / handling on the fly completions
        # See: keyPressEvent
        self._last_key_pressed_text = ''
        self.automatic_completions_after_chars = 3
        self.automatic_completions_after_ms = 300
        self._timer_key_press = QTimer(self)
        self._timer_key_press.setSingleShot(True)
        self._timer_key_press.timeout.connect(self._handle_completions)

        # Goto uri
        self._last_hover_pattern_key = None
        self._last_hover_pattern_text = None

        # 79-col edge line
        self.edge_line = self.panels.register(EdgeLine(self),
                                              Panel.Position.FLOATING)

        # indent guides
        self.indent_guides = self.panels.register(IndentationGuide(self),
                                                  Panel.Position.FLOATING)
        # Blanks enabled
        self.blanks_enabled = False

        # Underline errors and warnings
        self.underline_errors_enabled = False

        # Scrolling past the end of the document
        self.scrollpastend_enabled = False

        self.background = QColor('white')

        # Folding
        self.panels.register(FoldingPanel())

        # Debugger panel (Breakpoints)
        self.debugger = DebuggerManager(self)
        self.panels.register(DebuggerPanel())
        # Update breakpoints if the number of lines in the file changes
        self.blockCountChanged.connect(self.debugger.update_breakpoints)

        # Line number area management
        self.linenumberarea = self.panels.register(LineNumberArea(self))

        # Class and Method/Function Dropdowns
        self.classfuncdropdown = self.panels.register(
            ClassFunctionDropdown(self),
            Panel.Position.TOP,
        )

        # Colors to be defined in _apply_highlighter_color_scheme()
        # Currentcell color and current line color are defined in base.py
        self.occurrence_color = None
        self.ctrl_click_color = None
        self.sideareas_color = None
        self.matched_p_color = None
        self.unmatched_p_color = None
        self.normal_color = None
        self.comment_color = None

        # --- Syntax highlight entrypoint ---
        #
        # - if set, self.highlighter is responsible for
        #   - coloring raw text data inside editor on load
        #   - coloring text data when editor is cloned
        #   - updating document highlight on line edits
        #   - providing color palette (scheme) for the editor
        #   - providing data for Outliner
        # - self.highlighter is not responsible for
        #   - background highlight for current line
        #   - background highlight for search / current line occurrences

        self.highlighter_class = sh.TextSH
        self.highlighter = None
        ccs = 'Spyder'
        if ccs not in sh.COLOR_SCHEME_NAMES:
            ccs = sh.COLOR_SCHEME_NAMES[0]
        self.color_scheme = ccs

        self.highlight_current_line_enabled = False

        # Vertical scrollbar
        # This is required to avoid a "RuntimeError: no access to protected
        # functions or signals for objects not created from Python" in
        # Linux Ubuntu. See spyder-ide/spyder#5215.
        self.setVerticalScrollBar(QScrollBar())

        # Scrollbar flag area
        self.scrollflagarea = self.panels.register(ScrollFlagArea(self),
                                                   Panel.Position.RIGHT)
        self.scrollflagarea.hide()
        self.warning_color = "#FFAD07"
        self.error_color = "#EA2B0E"
        self.todo_color = "#B4D4F3"
        self.breakpoint_color = "#30E62E"

        self.panels.refresh()

        self.document_id = id(self)

        # Indicate occurrences of the selected word
        self.cursorPositionChanged.connect(self.__cursor_position_changed)
        self.__find_first_pos = None
        self.__find_flags = None

        self.language = None
        self.supported_language = False
        self.supported_cell_language = False
        self.classfunc_match = None
        self.comment_string = None
        self._kill_ring = QtKillRing(self)

        # Block user data
        self.blockCountChanged.connect(self.update_bookmarks)

        # Highlight using Pygments highlighter timer
        # ---------------------------------------------------------------------
        # For files that use the PygmentsSH we parse the full file inside
        # the highlighter in order to generate the correct coloring.
        self.timer_syntax_highlight = QTimer(self)
        self.timer_syntax_highlight.setSingleShot(True)
        # We wait 300 ms to trigger a new coloring as this value is a good
        # proxy for estimating when an user has stopped typing
        self.timer_syntax_highlight.setInterval(300)
        self.timer_syntax_highlight.timeout.connect(
            self.run_pygments_highlighter)

        # Mark occurrences timer
        self.occurrence_highlighting = None
        self.occurrence_timer = QTimer(self)
        self.occurrence_timer.setSingleShot(True)
        self.occurrence_timer.setInterval(1500)
        self.occurrence_timer.timeout.connect(self.__mark_occurrences)
        self.occurrences = []
        self.occurrence_color = QColor(Qt.yellow).lighter(160)

        # Mark found results
        self.textChanged.connect(self.__text_has_changed)
        self.found_results = []
        self.found_results_color = QColor(Qt.magenta).lighter(180)

        # Docstring
        self.writer_docstring = DocstringWriterExtension(self)

        # Context menu
        self.gotodef_action = None
        self.setup_context_menu()

        # Tab key behavior
        self.tab_indents = None
        self.tab_mode = True # see CodeEditor.set_tab_mode

        # Intelligent backspace mode
        self.intelligent_backspace = True

        # Automatic (on the fly) completions
        self.automatic_completions = True

        # Completions hint
        self.completions_hint = True

        self.close_parentheses_enabled = True
        self.close_quotes_enabled = False
        self.add_colons_enabled = True
        self.auto_unindent_enabled = True

        # Mouse tracking
        self.setMouseTracking(True)
        self.__cursor_changed = False
        self.ctrl_click_color = QColor(Qt.blue)

        self.bookmarks = self.get_bookmarks()

        # Keyboard shortcuts
        self.shortcuts = self.create_shortcuts()

        # Code editor
        self.__visible_blocks = []  # Visible blocks, update with repaint
        self.painted.connect(self._draw_editor_cell_divider)

        self.verticalScrollBar().valueChanged.connect(
                                       lambda value: self.rehighlight_cells())

        self.oe_proxy = None

        # Line stripping
        self.last_change_position = None
        self.last_position = None
        self.last_auto_indent = None
        self.skip_rstrip = False
        self.strip_trailing_spaces_on_modify = True

        # Hover hints
        self.hover_hints_enabled = None

        # Language Server
        self.lsp_requests = {}
        self.document_opened = False
        self.filename = None
        self.completions_available = False
        self.text_version = 0
        self.save_include_text = True
        self.open_close_notifications = True
        self.sync_mode = TextDocumentSyncKind.FULL
        self.will_save_notify = False
        self.will_save_until_notify = False
        self.enable_hover = True
        self.auto_completion_characters = []
        self.signature_completion_characters = []
        self.go_to_definition_enabled = False
        self.find_references_enabled = False
        self.highlight_enabled = False
        self.formatting_enabled = False
        self.range_formatting_enabled = False
        self.formatting_characters = []
        self.rename_support = False
        self.completion_args = None

        # Editor Extensions
        self.editor_extensions = EditorExtensionsManager(self)

        self.editor_extensions.add(CloseQuotesExtension())
        self.editor_extensions.add(SnippetsExtension())
        self.editor_extensions.add(CloseBracketsExtension())

        # Text diffs across versions
        self.differ = diff_match_patch()
        self.previous_text = ''
        self.word_tokens = []
        self.patch = []

        # Handle completions hints
        self.completion_widget.sig_completion_hint.connect(
            self.show_hint_for_completion)