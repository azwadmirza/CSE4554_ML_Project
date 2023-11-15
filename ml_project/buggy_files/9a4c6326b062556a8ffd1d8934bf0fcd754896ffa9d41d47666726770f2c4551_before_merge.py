def find_variable(var_name, caller_context, referenced_declaration=None):

    if isinstance(caller_context, Contract):
        function = None
        contract = caller_context
    elif isinstance(caller_context, Function):
        function = caller_context
        contract = function.contract
    else:
        logger.error('Incorrect caller context')
        exit(-1)

    if function:
        func_variables = function.variables_as_dict()
        if var_name in func_variables:
            return func_variables[var_name]
        # A local variable can be a pointer
        # for example
        # function test(function(uint) internal returns(bool) t) interna{
        # Will have a local variable t which will match the signature
        # t(uint256)
        func_variables_ptr = {get_pointer_name(f) : f for f in function.variables}
        if var_name and var_name in func_variables_ptr:
            return func_variables_ptr[var_name]

    contract_variables = contract.variables_as_dict()
    if var_name in contract_variables:
        return contract_variables[var_name]

    # A state variable can be a pointer
    conc_variables_ptr = {get_pointer_name(f) : f for f in contract.variables}
    if var_name and var_name in conc_variables_ptr:
        return conc_variables_ptr[var_name]


    functions = contract.functions_as_dict()
    if var_name in functions:
        return functions[var_name]

    modifiers = contract.modifiers_as_dict()
    if var_name in modifiers:
        return modifiers[var_name]

    structures = contract.structures_as_dict()
    if var_name in structures:
        return structures[var_name]

    events = contract.events_as_dict()
    if var_name in events:
        return events[var_name]

    enums = contract.enums_as_dict()
    if var_name in enums:
        return enums[var_name]

    # If the enum is refered as its name rather than its canonicalName
    enums = {e.name: e for e in contract.enums}
    if var_name in enums:
        return enums[var_name]

    # Could refer to any enum
    all_enums = [c.enums_as_dict() for c in contract.slither.contracts]
    all_enums = {k: v for d in all_enums for k, v in d.items()}
    if var_name in all_enums:
        return all_enums[var_name]

    if var_name in SOLIDITY_VARIABLES:
        return SolidityVariable(var_name)

    if var_name in SOLIDITY_FUNCTIONS:
        return SolidityFunction(var_name)

    contracts = contract.slither.contracts_as_dict()
    if var_name in contracts:
        return contracts[var_name]

    if referenced_declaration:
        for contract in contract.slither.contracts:
            if contract.id == referenced_declaration:
                return contract

    raise VariableNotFound('Variable not found: {}'.format(var_name))