def copy_ir(ir, *instances):
    '''
    Args:
        ir (Operation)
        local_variables_instances(dict(str -> LocalVariable))
        state_variables_instances(dict(str -> StateVariable))
        temporary_variables_instances(dict(int -> Variable))
        reference_variables_instances(dict(int -> Variable))

    Note: temporary and reference can be indexed by int, as they dont need phi functions
    '''
    if isinstance(ir, Assignment):
        lvalue = get_variable(ir, lambda x: x.lvalue, *instances)
        rvalue = get_variable(ir, lambda x: x.rvalue, *instances)
        variable_return_type = ir.variable_return_type
        return Assignment(lvalue, rvalue, variable_return_type)
    elif isinstance(ir, Balance):
        lvalue = get_variable(ir, lambda x: x.lvalue, *instances)
        value = get_variable(ir, lambda x: x.value, *instances)
        return Balance(value, lvalue)
    elif isinstance(ir, Binary):
        lvalue = get_variable(ir, lambda x: x.lvalue, *instances)
        variable_left = get_variable(ir, lambda x: x.variable_left, *instances)
        variable_right = get_variable(ir, lambda x: x.variable_right, *instances)
        operation_type = ir.type
        return Binary(lvalue, variable_left, variable_right, operation_type)
    elif isinstance(ir, Condition):
        val = get_variable(ir, lambda x: x.value, *instances)
        return Condition(val)
    elif isinstance(ir, Delete):
        lvalue = get_variable(ir, lambda x: x.lvalue, *instances)
        variable = get_variable(ir, lambda x: x.variable, *instances)
        return Delete(lvalue, variable)
    elif isinstance(ir, EventCall):
        name = ir.name
        return EventCall(name)
    elif isinstance(ir, HighLevelCall): # include LibraryCall
        destination = get_variable(ir, lambda x: x.destination, *instances)
        function_name = ir.function_name
        nbr_arguments = ir.nbr_arguments
        lvalue = get_variable(ir, lambda x: x.lvalue, *instances)
        type_call = ir.type_call
        if isinstance(ir, LibraryCall):
            new_ir = LibraryCall(destination, function_name, nbr_arguments, lvalue, type_call)
        else:
            new_ir = HighLevelCall(destination, function_name, nbr_arguments, lvalue, type_call)
        new_ir.call_id = ir.call_id
        new_ir.call_value = get_variable(ir, lambda x: x.call_value, *instances)
        new_ir.call_gas = get_variable(ir, lambda x: x.call_gas, *instances)
        new_ir.arguments = get_arguments(ir, *instances)
        new_ir.function = ir.function
        return new_ir
    elif isinstance(ir, Index):
        lvalue = get_variable(ir, lambda x: x.lvalue, *instances)
        variable_left = get_variable(ir, lambda x: x.variable_left, *instances)
        variable_right = get_variable(ir, lambda x: x.variable_right, *instances)
        index_type = ir.index_type
        return Index(lvalue, variable_left, variable_right, index_type)
    elif isinstance(ir, InitArray):
        lvalue = get_variable(ir, lambda x: x.lvalue, *instances)
        init_values = get_rec_values(ir, lambda x: x.init_values, *instances)
        return InitArray(init_values, lvalue)
    elif isinstance(ir, InternalCall):
        function = ir.function
        nbr_arguments = ir.nbr_arguments
        lvalue = get_variable(ir, lambda x: x.lvalue, *instances)
        type_call = ir.type_call
        new_ir = InternalCall(function, nbr_arguments, lvalue, type_call)
        new_ir.arguments = get_arguments(ir, *instances)
        return new_ir
    elif isinstance(ir, InternalDynamicCall):
        lvalue = get_variable(ir, lambda x: x.lvalue, *instances)
        function = get_variable(ir, lambda x: x.function, *instances)
        function_type = ir.function_type
        new_ir = InternalDynamicCall(lvalue, function, function_type)
        new_ir.arguments = get_arguments(ir, *instances)
        return new_ir
    elif isinstance(ir, LowLevelCall):
        destination = get_variable(ir, lambda x: x.destination, *instances)
        function_name = ir.function_name
        nbr_arguments = ir.nbr_arguments
        lvalue = get_variable(ir, lambda x: x.lvalue, *instances)
        type_call = ir.type_call
        new_ir = LowLevelCall(destination, function_name, nbr_arguments, lvalue, type_call)
        new_ir.call_id = ir.call_id
        new_ir.call_value = get_variable(ir, lambda x: x.call_value, *instances)
        new_ir.call_gas = get_variable(ir, lambda x: x.call_gas, *instances)
        new_ir.arguments = get_arguments(ir, *instances)
        return new_ir
    elif isinstance(ir, Member):
        lvalue = get_variable(ir, lambda x: x.lvalue, *instances)
        variable_left = get_variable(ir, lambda x: x.variable_left, *instances)
        variable_right = get_variable(ir, lambda x: x.variable_right, *instances)
        return Member(variable_left, variable_right, lvalue)
    elif isinstance(ir, NewArray):
        depth = ir.depth
        array_type = ir.array_type
        lvalue = get_variable(ir, lambda x: x.lvalue, *instances)
        new_ir = NewArray(depth, array_type, lvalue)
        new_ir.arguments = get_rec_values(ir, lambda x: x.arguments, *instances)
        return new_ir
    elif isinstance(ir, NewElementaryType):
        new_type = ir.type
        lvalue = get_variable(ir, lambda x: x.lvalue, *instances)
        new_ir = NewElementaryType(new_type, lvalue)
        new_ir.arguments = get_arguments(ir, *instances)
        return new_ir
    elif isinstance(ir, NewContract):
        contract_name = ir.contract_name
        lvalue = get_variable(ir, lambda x: x.lvalue, *instances)
        new_ir = NewContract(contract_name, lvalue)
        new_ir.arguments = get_arguments(ir, *instances)
        new_ir.call_value = get_variable(ir, lambda x: x.call_value, *instances)
        new_ir.call_salt = get_variable(ir, lambda x: x.call_salt, *instances)
        return new_ir
    elif isinstance(ir, NewStructure):
        structure = ir.structure
        lvalue = get_variable(ir, lambda x: x.lvalue, *instances)
        new_ir = NewStructure(structure, lvalue)
        new_ir.arguments = get_arguments(ir, *instances)
        return new_ir
    elif isinstance(ir, Nop):
        return Nop()
    elif isinstance(ir, Push):
        array = get_variable(ir, lambda x: x.array, *instances)
        lvalue = get_variable(ir, lambda x: x.lvalue, *instances)
        return Push(array, lvalue)
    elif isinstance(ir, Return):
        values = get_rec_values(ir, lambda x: x.values, *instances)
        return Return(values)
    elif isinstance(ir, Send):
        destination = get_variable(ir, lambda x: x.destination, *instances)
        value = get_variable(ir, lambda x: x.call_value, *instances)
        lvalue = get_variable(ir, lambda x: x.lvalue, *instances)
        return Send(destination, value, lvalue)
    elif isinstance(ir, SolidityCall):
        function = ir.function
        nbr_arguments = ir.nbr_arguments
        lvalue = get_variable(ir, lambda x: x.lvalue, *instances)
        type_call = ir.type_call
        new_ir = SolidityCall(function, nbr_arguments, lvalue, type_call)
        new_ir.arguments = get_arguments(ir, *instances)
        return new_ir
    elif isinstance(ir, Transfer):
        destination = get_variable(ir, lambda x: x.destination, *instances)
        value = get_variable(ir, lambda x: x.call_value, *instances)
        return Transfer(destination, value)
    elif isinstance(ir, TypeConversion):
        lvalue = get_variable(ir, lambda x: x.lvalue, *instances)
        variable = get_variable(ir, lambda x: x.variable, *instances)
        variable_type = ir.type
        return TypeConversion(lvalue, variable, variable_type)
    elif isinstance(ir, Unary):
        lvalue = get_variable(ir, lambda x: x.lvalue, *instances)
        rvalue = get_variable(ir, lambda x: x.rvalue, *instances)
        operation_type = ir.type
        return Unary(lvalue, rvalue, operation_type)
    elif isinstance(ir, Unpack):
        lvalue = get_variable(ir, lambda x: x.lvalue, *instances)
        tuple_var = get_variable(ir, lambda x: x.tuple, *instances)
        idx = ir.index
        return Unpack(lvalue, tuple_var, idx)
    elif isinstance(ir, Length):
        lvalue = get_variable(ir, lambda x: x.lvalue, *instances)
        value = get_variable(ir, lambda x: x.value, *instances)
        return Length(value, lvalue)


    raise SlithIRError('Impossible ir copy on {} ({})'.format(ir, type(ir)))