    def _construct_parser(self, fname):
        # type: (str) -> RawConfigParser
        parser = configparser.RawConfigParser()
        # If there is no such file, don't bother reading it but create the
        # parser anyway, to hold the data.
        # Doing this is useful when modifying and saving files, where we don't
        # need to construct a parser.
        if os.path.exists(fname):
            try:
                parser.read(fname)
            except UnicodeDecodeError:
                raise ConfigurationError((
                    "ERROR: "
                    "Configuration file contains invalid %s characters.\n"
                    "Please fix your configuration, located at %s\n"
                ) % (locale.getpreferredencoding(False), fname))
        return parser