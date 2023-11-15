    def __init__(self, schema, graphiql=True):
        self.schema = schema
        self.graphiql = graphiql

        if not self.schema:
            raise ValueError("You must pass in a schema to GraphQLView")

        if not isinstance(self.schema, GraphQLSchema):
            raise ValueError("A valid schema is required to be provided to GraphQLView")