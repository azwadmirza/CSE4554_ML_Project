    def input_value_definition(self, tree: Tree) -> GraphQLArgument:
        # TODO: Add directives
        description = None
        name = None
        gql_type = None
        default_value = None
        directives = None
        for child in tree.children:
            if child.type == "description":
                description = child.value
            elif child.type == "IDENT":
                name = child.value
            elif child.type == "type":
                gql_type = child.value
            elif child.type == "value":
                default_value = child.value
            elif child.type == "discard":
                pass
            elif child.type == "directives":
                directives = child.value
            else:
                raise UnexpectedASTNode(
                    "Unexpected AST node `{}`, type `{}`".format(
                        child, child.__class__.__name__
                    )
                )
        return GraphQLArgument(
            name=name,
            gql_type=gql_type,
            default_value=default_value,
            description=description,
            directives=directives,
        )