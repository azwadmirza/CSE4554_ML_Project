    def _wrap(func):
        directive_name = name or to_camel_case(func.__name__)

        func.directive = GraphQLDirective(
            name=directive_name,
            locations=locations,
            args=_get_arguments(func),
            description=description,
        )

        DIRECTIVE_REGISTRY[directive_name] = func

        return func