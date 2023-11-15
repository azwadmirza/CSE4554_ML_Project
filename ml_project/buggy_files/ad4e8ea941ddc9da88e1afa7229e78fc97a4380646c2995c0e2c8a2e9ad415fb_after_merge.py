    def touch(self, times=None):
        """ times must be 2-tuple: (atime, mtime) """
        try:
            if self.is_directory:
                file = os.path.join(self.file, TIMESTAMP_FILENAME)
                # Create the flag file if it doesn't exist
                if not os.path.exists(file):
                    with open(file, "w") as f:
                        pass
                lutime(file, times)
            else:
                lutime(self.file, times)
        except OSError as e:
            if e.errno == 2:
                raise MissingOutputException(
                    "Output file {} of rule {} shall be touched but "
                    "does not exist.".format(self.file, self.rule.name),
                    lineno=self.rule.lineno,
                    snakefile=self.rule.snakefile,
                )
            else:
                raise e