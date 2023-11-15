    def read(self, filenames):
        # RawConfigParser takes a filename or list of filenames, but we only
        # ever call this with a single filename.
        assert isinstance(filenames, path_types)
        filename = filenames
        if env.PYVERSION >= (3, 6):
            filename = os.fspath(filename)

        try:
            with io.open(filename, encoding='utf-8') as fp:
                toml_text = fp.read()
        except IOError:
            return []
        if toml:
            toml_text = substitute_variables(toml_text, os.environ)
            try:
                self.data = toml.loads(toml_text)
            except toml.TomlDecodeError as err:
                raise TomlDecodeError(*err.args)
            return [filename]
        else:
            has_toml = re.search(r"^\[tool\.coverage\.", toml_text, flags=re.MULTILINE)
            if self.our_file or has_toml:
                # Looks like they meant to read TOML, but we can't read it.
                msg = "Can't read {!r} without TOML support. Install with [toml] extra"
                raise CoverageException(msg.format(filename))
            return []