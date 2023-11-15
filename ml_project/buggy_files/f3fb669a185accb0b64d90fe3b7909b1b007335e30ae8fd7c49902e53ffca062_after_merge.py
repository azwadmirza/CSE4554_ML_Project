    def __init__(self, document, builder):
        nodes.NodeVisitor.__init__(self, document)
        self.builder = builder
        self.body = []

        # sort out some elements
        papersize = builder.config.latex_paper_size + 'paper'
        if papersize == 'paper': # e.g. command line "-D latex_paper_size="
            papersize = 'letterpaper'

        self.elements = self.default_elements.copy()
        self.elements.update({
            'wrapperclass': self.format_docclass(document.settings.docclass),
            'papersize':    papersize,
            'pointsize':    builder.config.latex_font_size,
            # if empty, the title is set to the first section title
            'title':        document.settings.title,
            'release':      builder.config.release,
            'author':       document.settings.author,
            'releasename':  _('Release'),
            'preamble':     builder.config.latex_preamble,
            'indexname':    _('Index'),
        })
        if document.settings.docclass == 'howto':
            docclass = builder.config.latex_docclass.get('howto', 'article')
        else:
            docclass = builder.config.latex_docclass.get('manual', 'report')
        self.elements['docclass'] = docclass
        if builder.config.today:
            self.elements['date'] = builder.config.today
        else:
            self.elements['date'] = ustrftime(builder.config.today_fmt
                                              or _('%B %d, %Y'))
        if builder.config.latex_logo:
            self.elements['logo'] = '\\includegraphics{%s}\\par' % \
                                    path.basename(builder.config.latex_logo)
        if builder.config.language:
            babel = ExtBabel(builder.config.language)
            lang = babel.get_language()
            if lang:
                self.elements['classoptions'] += ',' + babel.get_language()
            else:
                self.builder.warn('no Babel option known for language %r' %
                                  builder.config.language)
            self.elements['shorthandoff'] = babel.get_shorthandoff()
            self.elements['fncychap'] = '\\usepackage[Sonny]{fncychap}'

            # Times fonts don't work with Cyrillic languages
            if babel.uses_cyrillic():
                self.elements['fontpkg'] = ''

            # pTeX (Japanese TeX) for support
            if builder.config.language == 'ja':
                # use dvipdfmx as default class option in Japanese
                self.elements['classoptions'] = ',dvipdfmx'
                # disable babel which has not publishing quality in Japanese
                self.elements['babel'] = ''
                # disable fncychap in Japanese documents
                self.elements['fncychap'] = ''
        else:
            self.elements['classoptions'] += ',english'
        if getattr(builder, 'usepackages', None):
            usepackages = ('\\usepackage{%s}' % p for p in builder.usepackages)
            self.elements['usepackages'] += "\n".join(usepackages)
        # allow the user to override them all
        self.elements.update(builder.config.latex_elements)
        if self.elements['extraclassoptions']:
            self.elements['classoptions'] += ',' + \
                                             self.elements['extraclassoptions']

        self.highlighter = highlighting.PygmentsBridge('latex',
            builder.config.pygments_style, builder.config.trim_doctest_flags)
        self.context = []
        self.descstack = []
        self.bibitems = []
        self.table = None
        self.next_table_colspec = None
        # stack of [language, linenothreshold] settings per file
        # the first item here is the default and must not be changed
        # the second item is the default for the master file and can be changed
        # by .. highlight:: directive in the master file
        self.hlsettingstack = 2 * [[builder.config.highlight_language,
                                    sys.maxsize]]
        self.footnotestack = []
        self.curfilestack = []
        self.handled_abbrs = set()
        if document.settings.docclass == 'howto':
            self.top_sectionlevel = 2
        else:
            if builder.config.latex_use_parts:
                self.top_sectionlevel = 0
            else:
                self.top_sectionlevel = 1
        self.next_section_ids = set()
        self.next_figure_ids = set()
        self.next_table_ids = set()
        self.next_literal_ids = set()
        # flags
        self.in_title = 0
        self.in_production_list = 0
        self.in_footnote = 0
        self.in_caption = 0
        self.first_document = 1
        self.this_is_the_title = 1
        self.literal_whitespace = 0
        self.no_contractions = 0
        self.compact_list = 0
        self.first_param = 0
        self.previous_spanning_row = 0
        self.previous_spanning_column = 0
        self.remember_multirow = {}