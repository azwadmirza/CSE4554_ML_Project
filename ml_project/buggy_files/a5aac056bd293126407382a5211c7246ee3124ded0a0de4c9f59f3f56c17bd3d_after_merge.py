def _surround_with_execution_directives(
    func: Callable, directives: list
) -> Callable:
    for directive in reversed(directives):
        func = partial(
            directive["callables"].on_field_execution, directive["args"], func
        )
    return func