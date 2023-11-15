    def __init__(
        self,
        schema: BaseSchema,
        graphiql: bool = True,
        root_value: Optional[Any] = None,
    ):
        self.graphiql = graphiql
        self.schema = schema
        self.root_value = root_value