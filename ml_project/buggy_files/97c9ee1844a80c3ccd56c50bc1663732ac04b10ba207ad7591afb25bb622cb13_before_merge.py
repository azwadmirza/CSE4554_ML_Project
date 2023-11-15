    async def create_connection(self, with_db: bool) -> None:
        self._template = {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "db": self.database if with_db else None,
            "autocommit": True,
            **self.extra,
        }
        try:
            self._connection = await aiomysql.connect(password=self.password, **self._template)
            self.log.debug(
                "Created connection %s with params: %s", self._connection, self._template
            )
        except pymysql.err.OperationalError:
            raise DBConnectionError(
                "Can't connect to MySQL server: {template}".format(template=self._template)
            )