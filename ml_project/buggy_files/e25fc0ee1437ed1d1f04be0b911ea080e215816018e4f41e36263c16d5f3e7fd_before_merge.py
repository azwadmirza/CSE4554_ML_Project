    def __init__(self, module=None):
        self.title = "Overview"
        self.parts = []
        self.parts_by_slug = {}
        self.doc_dir = None
        self.xml_data_file = None
        self.tex_data_file = None
        self.latex_file = None
        self.symbols = {}
        if module is None:
            return

        import importlib

        # Load the module and verifies it is a pymathics module
        try:
            self.pymathicsmodule = importlib.import_module(module)
        except ImportError:
            print("Module does not exist")
            mainfolder = ""
            self.pymathicsmodule = None
            self.parts = []
            return

        if hasattr(self.pymathicsmodule, "pymathics_version_data"):
            mainfolder = self.pymathicsmodule.__path__[0]
            self.name = self.pymathicsmodule.pymathics_version_data['name']
            self.version = self.pymathicsmodule.pymathics_version_data['version']
            self.author = self.pymathicsmodule.pymathics_version_data['author']
        else:
            print(module + " is not a pymathics module.")
            mainfolder = ""
            self.pymathicsmodule = None
            self.parts = []
            return

        # Paths
        self.doc_dir = self.pymathicsmodule.__path__[0] + "/doc/"
        self.xml_data_file = self.doc_dir + "xml/data"
        self.tex_data_file = self.doc_dir + "tex/data"
        self.latex_file = self.doc_dir + "tex/documentation.tex"

        # Load the dictionary of mathics symbols defined in the module
        self.symbols = {}
        from mathics.builtin import is_builtin, Builtin
        print("loading symbols")
        for name in dir(self.pymathicsmodule):
            var = getattr(self.pymathicsmodule, name)
            if (hasattr(var, '__module__') and
                var.__module__ != 'mathics.builtin.base' and 
                    is_builtin(var) and not name.startswith('_') and
                var.__module__[:len(self.pymathicsmodule.__name__)] == self.pymathicsmodule.__name__):     # nopep8
                instance = var(expression=False)
                if isinstance(instance, Builtin):
                    self.symbols[instance.get_name()] = instance
        # Defines de default first part, in case we are building an independent documentation module.
        self.title = "Overview"
        self.parts = []
        self.parts_by_slug = {}
        try:
            files = listdir(self.doc_dir)
            files.sort()
        except FileNotFoundError:
            self.doc_dir = ""
            self.xml_data_file = ""
            self.tex_data_file = ""
            self.latex_file = ""
            files = []
        appendix = []
        for file in files:
            part_title = file[2:]
            if part_title.endswith('.mdoc'):
                part_title = part_title[:-len('.mdoc')]
                part = DocPart(self, part_title)
                text = open(self.doc_dir + file, 'rb').read().decode('utf8')
                text = filter_comments(text)
                chapters = CHAPTER_RE.findall(text)
                for title, text in chapters:
                    chapter = DocChapter(part, title)
                    text += '<section title=""></section>'
                    sections = SECTION_RE.findall(text)
                    for pre_text, title, text in sections:
                        if not chapter.doc:
                            chapter.doc = Doc(pre_text)
                        if title:
                            section = DocSection(chapter, title, text)
                            chapter.sections.append(section)
                    part.chapters.append(chapter)
                if file[0].isdigit():
                    self.parts.append(part)
                else:
                    part.is_appendix = True
                    appendix.append(part)

        # Builds the automatic documentation
        builtin_part = DocPart(self, "Pymathics Modules", is_reference=True)
        title, text = get_module_doc(self.pymathicsmodule)
        chapter = DocChapter(builtin_part, title, Doc(text))
        for name in self.symbols:
            instance = self.symbols[name]
            installed = True
            for package in getattr(instance, 'requires', []):
                try:
                    importlib.import_module(package)
                except ImportError:
                    installed = False
                    break
            section = DocSection(
                chapter, strip_system_prefix(name),
                instance.__doc__ or '',
                operator=instance.get_operator(),
                installed=installed)
            chapter.sections.append(section)
        builtin_part.chapters.append(chapter)
        self.parts.append(builtin_part)
        # Adds possible appendices
        for part in appendix:
            self.parts.append(part)

        # set keys of tests
        for tests in self.get_tests():
            for test in tests.tests:
                test.key = (
                    tests.part, tests.chapter, tests.section, test.index)