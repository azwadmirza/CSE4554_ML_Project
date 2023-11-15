    def __connect(self, first_connect_check=False):
        pool = self.__pool

        # ensure any existing connection is removed, so that if
        # creator fails, this attribute stays None
        self.connection = None
        try:
            self.starttime = time.time()
            connection = pool._invoke_creator(self)
            pool.logger.debug("Created new connection %r", connection)
            self.connection = connection
        except Exception as e:
            pool.logger.debug("Error on connect(): %s", e)
            raise
        else:
            if first_connect_check:
                pool.dispatch.first_connect.for_modify(
                    pool.dispatch
                ).exec_once(self.connection, self)
            if pool.dispatch.connect:
                pool.dispatch.connect(self.connection, self)