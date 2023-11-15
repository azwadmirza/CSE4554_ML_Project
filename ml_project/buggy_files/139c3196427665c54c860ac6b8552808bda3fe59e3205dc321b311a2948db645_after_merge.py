    def __init__(
        self,
        schema: BaseSchema,
        root_value: typing.Any = None,
        graphiql: bool = True,
        keep_alive: bool = False,
        keep_alive_interval: float = 1,
        debug: bool = False,
    ) -> None:
        self.schema = schema
        self.graphiql = graphiql
        self.root_value = root_value
        self.keep_alive = keep_alive
        self.keep_alive_interval = keep_alive_interval
        self._keep_alive_task = None
        self.debug = debug