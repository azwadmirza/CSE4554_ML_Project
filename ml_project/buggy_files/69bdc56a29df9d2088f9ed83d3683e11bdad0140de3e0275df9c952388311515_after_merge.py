    def parse_file(self) -> None:
        if self.tree is not None:
            # The file was already parsed (in __init__()).
            return

        manager = self.manager
        modules = manager.modules
        manager.log("Parsing %s (%s)" % (self.xpath, self.id))

        with self.wrap_context():
            source = self.source
            self.source = None  # We won't need it again.
            if self.path and source is None:
                try:
                    source = read_with_python_encoding(self.path, manager.pyversion)
                except IOError as ioerr:
                    raise CompileError([
                        "mypy: can't read file '{}': {}".format(self.path, ioerr.strerror)])
                except (UnicodeDecodeError, DecodeError) as decodeerr:
                    raise CompileError([
                        "mypy: can't decode file '{}': {}".format(self.path, str(decodeerr))])
            self.tree = manager.parse_file(self.id, self.xpath, source)

        modules[self.id] = self.tree

        # Do the first pass of semantic analysis: add top-level
        # definitions in the file to the symbol table.  We must do
        # this before processing imports, since this may mark some
        # import statements as unreachable.
        first = FirstPass(manager.semantic_analyzer)
        first.analyze(self.tree, self.xpath, self.id)

        # Initialize module symbol table, which was populated by the
        # semantic analyzer.
        # TODO: Why can't FirstPass .analyze() do this?
        self.tree.names = manager.semantic_analyzer.globals

        # Compute (direct) dependencies.
        # Add all direct imports (this is why we needed the first pass).
        # Also keep track of each dependency's source line.
        dependencies = []
        suppressed = []
        dep_line_map = {}  # type: Dict[str, int]  # id -> line
        for id, line in manager.all_imported_modules_in_file(self.tree):
            if id == self.id:
                continue
            # Omit missing modules, as otherwise we could not type-check
            # programs with missing modules.
            if id in manager.missing_modules:
                if id not in dep_line_map:
                    suppressed.append(id)
                    dep_line_map[id] = line
                continue
            if id == '':
                # Must be from a relative import.
                manager.errors.set_file(self.xpath)
                manager.errors.report(line, "No parent module -- cannot perform relative import",
                                      blocker=True)
                continue
            if id not in dep_line_map:
                dependencies.append(id)
                dep_line_map[id] = line
        # Every module implicitly depends on builtins.
        if self.id != 'builtins' and 'builtins' not in dep_line_map:
            dependencies.append('builtins')

        # If self.dependencies is already set, it was read from the
        # cache, but for some reason we're re-parsing the file.
        # NOTE: What to do about race conditions (like editing the
        # file while mypy runs)?  A previous version of this code
        # explicitly checked for this, but ran afoul of other reasons
        # for differences (e.g. --silent-imports).
        self.dependencies = dependencies
        self.suppressed = suppressed
        self.dep_line_map = dep_line_map
        self.check_blockers()