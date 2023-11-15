    def open(self):
        """Open the resource as "io.open" does

        Raises:
            FrictionlessException: any exception that occurs
        """
        self.close()

        # Infer
        self.pop("stats", None)
        self["name"] = self.name
        self["profile"] = self.profile
        self["scheme"] = self.scheme
        self["format"] = self.format
        self["hashing"] = self.hashing
        self["encoding"] = self.encoding
        if self.innerpath:
            self["innerpath"] = self.innerpath
        if self.compression:
            self["compression"] = self.compression
        if self.control:
            self["control"] = self.control
        if self.dialect:
            self["dialect"] = self.dialect
        self["stats"] = self.stats

        # Validate
        if self.metadata_errors:
            error = self.metadata_errors[0]
            raise FrictionlessException(error)

        # Open
        try:

            # Table
            if self.tabular:
                self.__parser = system.create_parser(self)
                self.__parser.open()
                self.__read_detect_layout()
                self.__read_detect_schema()
                if not self.__nolookup:
                    self.__lookup = self.__read_detect_lookup()
                self.__header = self.__read_header()
                self.__row_stream = self.__read_row_stream()
                return self

            # File
            else:
                self.__loader = system.create_loader(self)
                self.__loader.open()
                return self

        # Error
        except Exception:
            self.close()
            raise