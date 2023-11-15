    def __init__(self, name, inicontents='', separator='=', commenter='#'):
        super(_Section, self).__init__(self)
        self.name = name
        self.inicontents = inicontents
        self.sep = separator
        self.com = commenter

        opt_regx_prefix = r'(\s*)(.+?)\s*'
        opt_regx_suffix = r'\s*(.*)\s*'
        self.opt_regx_str = r'{0}(\{1}){2}'.format(
            opt_regx_prefix, self.sep, opt_regx_suffix
        )
        self.opt_regx = re.compile(self.opt_regx_str)