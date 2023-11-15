    def __init__(self, schema=None, graphiql=True):
        if not schema:
            raise ValueError("You must pass in a schema to GraphQLView")

        if not isinstance(schema, GraphQLSchema):
            raise ValueError("You must pass in a valid schema to GraphQLView")

        self.schema = schema
        self.graphiql = graphiql