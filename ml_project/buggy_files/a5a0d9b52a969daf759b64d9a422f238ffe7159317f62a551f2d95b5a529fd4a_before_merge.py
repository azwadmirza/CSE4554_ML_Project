def parse_yul_identifier(root: YulScope, node: YulNode, ast: Dict) -> Optional[Expression]:
    name = ast['name']

    if name in builtins:
        return Identifier(YulBuiltin(name))

    # check function-scoped variables
    if root.parent_func:
        variable = root.parent_func.get_local_variable_from_name(name)
        if variable:
            return Identifier(variable)

    # check yul-scoped variable
    variable = root.get_yul_local_variable_from_name(name)
    if variable:
        return Identifier(variable.underlying)

    # check yul-scoped function

    func = root.get_yul_local_function_from_name(name)
    if func:
        return Identifier(func.underlying)

    # check for magic suffixes
    if name.endswith("_slot"):
        potential_name = name[:-5]
        var = root.function.contract.get_state_variable_from_name(potential_name)
        if var:
            return Identifier(SolidityVariable(name))
    if name.endswith("_offset"):
        potential_name = name[:-7]
        var = root.function.contract.get_state_variable_from_name(potential_name)
        if var:
            return Identifier(SolidityVariable(name))

    raise SlitherException(f"unresolved reference to identifier {name}")