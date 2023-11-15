    async def create_connection(self, with_db: bool) -> None:
        self._template = {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "database": self.database if with_db else None,
            **self.extra,
        }
        try:
            self._connection = await asyncpg.connect(None, password=self.password, **self._template)
            self.log.debug(
                "Created connection %s with params: %s", self._connection, self._template
            )
        except asyncpg.InvalidCatalogNameError:
            raise DBConnectionError(
                "Can't establish connection to database {}".format(self.database)
            )