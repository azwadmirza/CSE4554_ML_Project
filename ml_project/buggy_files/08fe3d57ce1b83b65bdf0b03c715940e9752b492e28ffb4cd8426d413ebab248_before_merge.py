    def __init__(self, parent, font=None, color_scheme='Spyder'):
        QSyntaxHighlighter.__init__(self, parent)

        self.font = font
        if is_text_string(color_scheme):
            self.color_scheme = get_color_scheme(color_scheme)
        else:
            self.color_scheme = color_scheme

        self.background_color = None
        self.currentline_color = None
        self.currentcell_color = None
        self.occurrence_color = None
        self.ctrlclick_color = None
        self.sideareas_color = None
        self.matched_p_color = None
        self.unmatched_p_color = None

        self.formats = None
        self.setup_formats(font)

        self.cell_separators = None
        self.request_folding = True
        self.editor = None
        self.patterns = DEFAULT_COMPILED_PATTERNS