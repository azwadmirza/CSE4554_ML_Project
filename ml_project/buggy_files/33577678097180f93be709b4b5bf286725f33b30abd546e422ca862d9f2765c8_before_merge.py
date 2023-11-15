    def _create_engine(self):
        log.info("using the connect string {0!s}".format(censor_connect_string(self.connect_string)))
        try:
            log.debug("using pool_size={0!s}, pool_timeout={1!s}, pool_recycle={2!s}".format(
                self.pool_size, self.pool_timeout, self.pool_recycle))
            engine = create_engine(self.connect_string,
                                        encoding=self.encoding,
                                        convert_unicode=False,
                                        pool_size=self.pool_size,
                                        pool_recycle=self.pool_recycle,
                                        pool_timeout=self.pool_timeout)
        except TypeError:
            # The DB Engine/Poolclass might not support the pool_size.
            log.debug("connecting without pool_size.")
            engine = create_engine(self.connect_string,
                                        encoding=self.encoding,
                                        convert_unicode=False)
        return engine