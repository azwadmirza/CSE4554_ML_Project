    def __init__(self, pyversion: Tuple[int, int] = defaults.PYTHON3_VERSION,
                 is_stub_file: bool = False) -> None:
        self.map = {}
        self.tok = []
        self.indents = [0]
        self.open_brackets = []
        self.pyversion = pyversion
        self.is_stub_file = is_stub_file
        self.ignored_lines = set()
        # Fill in the map from valid character codes to relevant lexer methods.
        extra_misc = '' if pyversion[0] >= 3 else '`'
        for seq, method in [('ABCDEFGHIJKLMNOPQRSTUVWXYZ', self.lex_name),
                            ('abcdefghijklmnopqrstuvwxyz_', self.lex_name),
                            ('0123456789', self.lex_number),
                            ('.', self.lex_number_or_dot),
                            (' ' + '\t' + '\x0c', self.lex_space),
                            ('"', self.lex_str_double),
                            ("'", self.lex_str_single),
                            ('\r' + '\n', self.lex_break),
                            (';', self.lex_semicolon),
                            (':', self.lex_colon),
                            ('#', self.lex_comment),
                            ('\\', self.lex_backslash),
                            ('([{', self.lex_open_bracket),
                            (')]}', self.lex_close_bracket),
                            ('-+*/<>%&|^~=!,@' + extra_misc, self.lex_misc)]:
            for c in seq:
                self.map[c] = method
        if pyversion[0] == 2:
            self.keywords = keywords_common | keywords2
            # Decimal/hex/octal/binary literal or integer complex literal
            self.number_exp1 = re.compile('(0[xXoObB][0-9a-fA-F]+|[0-9]+)[lL]?')

        if pyversion[0] == 3:
            self.keywords = keywords_common | keywords3
            self.number_exp1 = re.compile('0[xXoObB][0-9a-fA-F]+|[0-9]+')