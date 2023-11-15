def propagate_types(ir, node):  # pylint: disable=too-many-locals
    # propagate the type
    using_for = node.function.contract.using_for
    if isinstance(ir, OperationWithLValue):
        # Force assignment in case of missing previous correct type
        if not ir.lvalue.type:
            if isinstance(ir, Assignment):
                ir.lvalue.set_type(ir.rvalue.type)
            elif isinstance(ir, Binary):
                if BinaryType.return_bool(ir.type):
                    ir.lvalue.set_type(ElementaryType("bool"))
                else:
                    ir.lvalue.set_type(ir.variable_left.type)
            elif isinstance(ir, Delete):
                # nothing to propagate
                pass
            elif isinstance(ir, LibraryCall):
                return convert_type_library_call(ir, ir.destination)
            elif isinstance(ir, HighLevelCall):
                t = ir.destination.type

                # Temporary operation (they are removed later)
                if t is None:
                    return None

                if isinstance(t, ElementaryType) and t.name == "address":
                    if can_be_solidity_func(ir):
                        return convert_to_solidity_func(ir)

                # convert library
                if t in using_for or "*" in using_for:
                    new_ir = convert_to_library(ir, node, using_for)
                    if new_ir:
                        return new_ir

                if isinstance(t, UserDefinedType):
                    # UserdefinedType
                    t_type = t.type
                    if isinstance(t_type, Contract):
                        contract = node.slither.get_contract_from_name(t_type.name)
                        return convert_type_of_high_and_internal_level_call(ir, contract)

                # Convert HighLevelCall to LowLevelCall
                if isinstance(t, ElementaryType) and t.name == "address":
                    if ir.destination.name == "this":
                        return convert_type_of_high_and_internal_level_call(
                            ir, node.function.contract
                        )
                    if can_be_low_level(ir):
                        return convert_to_low_level(ir)

                # Convert push operations
                # May need to insert a new operation
                # Which leads to return a list of operation
                if isinstance(t, ArrayType) or (
                    isinstance(t, ElementaryType) and t.type == "bytes"
                ):
                    if ir.function_name == "push" and len(ir.arguments) == 1:
                        return convert_to_push(ir, node)
                    if ir.function_name == "pop" and len(ir.arguments) == 0:
                        return convert_to_pop(ir, node)

            elif isinstance(ir, Index):
                if isinstance(ir.variable_left.type, MappingType):
                    ir.lvalue.set_type(ir.variable_left.type.type_to)
                elif isinstance(ir.variable_left.type, ArrayType):
                    ir.lvalue.set_type(ir.variable_left.type.type)

            elif isinstance(ir, InitArray):
                length = len(ir.init_values)
                t = ir.init_values[0].type
                ir.lvalue.set_type(ArrayType(t, length))
            elif isinstance(ir, InternalCall):
                # if its not a tuple, return a singleton
                if ir.function is None:
                    convert_type_of_high_and_internal_level_call(ir, node.function.contract)
                return_type = ir.function.return_type
                if return_type:
                    if len(return_type) == 1:
                        ir.lvalue.set_type(return_type[0])
                    elif len(return_type) > 1:
                        ir.lvalue.set_type(return_type)
                else:
                    ir.lvalue = None
            elif isinstance(ir, InternalDynamicCall):
                # if its not a tuple, return a singleton
                return_type = ir.function_type.return_type
                if return_type:
                    if len(return_type) == 1:
                        ir.lvalue.set_type(return_type[0])
                    else:
                        ir.lvalue.set_type(return_type)
                else:
                    ir.lvalue = None
            elif isinstance(ir, LowLevelCall):
                # Call are not yet converted
                # This should not happen
                assert False
            elif isinstance(ir, Member):
                # TODO we should convert the reference to a temporary if the member is a length or a balance
                if (
                    ir.variable_right == "length"
                    and not isinstance(ir.variable_left, Contract)
                    and isinstance(ir.variable_left.type, (ElementaryType, ArrayType))
                ):
                    length = Length(ir.variable_left, ir.lvalue)
                    length.set_expression(ir.expression)
                    length.lvalue.points_to = ir.variable_left
                    length.set_node(ir.node)
                    return length
                if (
                    ir.variable_right == "balance"
                    and not isinstance(ir.variable_left, Contract)
                    and isinstance(ir.variable_left.type, ElementaryType)
                ):
                    b = Balance(ir.variable_left, ir.lvalue)
                    b.set_expression(ir.expression)
                    b.set_node(ir.node)
                    return b
                if (
                    ir.variable_right == "codesize"
                    and not isinstance(ir.variable_left, Contract)
                    and isinstance(ir.variable_left.type, ElementaryType)
                ):
                    b = CodeSize(ir.variable_left, ir.lvalue)
                    b.set_expression(ir.expression)
                    b.set_node(ir.node)
                    return b
                if ir.variable_right == "selector" and isinstance(ir.variable_left.type, Function):
                    assignment = Assignment(
                        ir.lvalue,
                        Constant(str(get_function_id(ir.variable_left.type.full_name))),
                        ElementaryType("bytes4"),
                    )
                    assignment.set_expression(ir.expression)
                    assignment.set_node(ir.node)
                    assignment.lvalue.set_type(ElementaryType("bytes4"))
                    return assignment
                if isinstance(ir.variable_left, TemporaryVariable) and isinstance(
                    ir.variable_left.type, TypeInformation
                ):
                    return _convert_type_contract(ir, node.function.slither)
                left = ir.variable_left
                t = None
                # Handling of this.function_name usage
                if (
                    left == SolidityVariable("this")
                    and isinstance(ir.variable_right, Constant)
                    and str(ir.variable_right) in [x.name for x in ir.function.contract.functions]
                ):
                    # Assumption that this.function_name can only compile if
                    # And the contract does not have two functions starting with function_name
                    # Otherwise solc raises:
                    # Error: Member "f" not unique after argument-dependent lookup in contract
                    targeted_function = next(
                        (
                            x
                            for x in ir.function.contract.functions
                            if x.name == str(ir.variable_right)
                        )
                    )
                    t = _make_function_type(targeted_function)
                    ir.lvalue.set_type(t)
                elif isinstance(left, (Variable, SolidityVariable)):
                    t = ir.variable_left.type
                elif isinstance(left, (Contract, Enum, Structure)):
                    t = UserDefinedType(left)
                # can be None due to temporary operation
                if t:
                    if isinstance(t, UserDefinedType):
                        # UserdefinedType
                        type_t = t.type
                        if isinstance(type_t, Enum):
                            ir.lvalue.set_type(t)
                        elif isinstance(type_t, Structure):
                            elems = type_t.elems
                            for elem in elems:
                                if elem == ir.variable_right:
                                    ir.lvalue.set_type(elems[elem].type)
                        else:
                            assert isinstance(type_t, Contract)
                            # Allow type propagtion as a Function
                            # Only for reference variables
                            # This allows to track the selector keyword
                            # We dont need to check for function collision, as solc prevents the use of selector
                            # if there are multiple functions with the same name
                            f = next(
                                (f for f in type_t.functions if f.name == ir.variable_right),
                                None,
                            )
                            if f:
                                ir.lvalue.set_type(f)
                            else:
                                # Allow propgation for variable access through contract's nale
                                # like Base_contract.my_variable
                                v = next(
                                    (
                                        v
                                        for v in type_t.state_variables
                                        if v.name == ir.variable_right
                                    ),
                                    None,
                                )
                                if v:
                                    ir.lvalue.set_type(v.type)
            elif isinstance(ir, NewArray):
                ir.lvalue.set_type(ir.array_type)
            elif isinstance(ir, NewContract):
                contract = node.slither.get_contract_from_name(ir.contract_name)
                ir.lvalue.set_type(UserDefinedType(contract))
            elif isinstance(ir, NewElementaryType):
                ir.lvalue.set_type(ir.type)
            elif isinstance(ir, NewStructure):
                ir.lvalue.set_type(UserDefinedType(ir.structure))
            elif isinstance(ir, Push):
                # No change required
                pass
            elif isinstance(ir, Send):
                ir.lvalue.set_type(ElementaryType("bool"))
            elif isinstance(ir, SolidityCall):
                if ir.function.name in ["type(address)", "type()"]:
                    ir.function.return_type = [TypeInformation(ir.arguments[0])]
                return_type = ir.function.return_type
                if len(return_type) == 1:
                    ir.lvalue.set_type(return_type[0])
                elif len(return_type) > 1:
                    ir.lvalue.set_type(return_type)
            elif isinstance(ir, TypeConversion):
                ir.lvalue.set_type(ir.type)
            elif isinstance(ir, Unary):
                ir.lvalue.set_type(ir.rvalue.type)
            elif isinstance(ir, Unpack):
                types = ir.tuple.type.type
                idx = ir.index
                t = types[idx]
                ir.lvalue.set_type(t)
            elif isinstance(
                ir,
                (
                    Argument,
                    TmpCall,
                    TmpNewArray,
                    TmpNewContract,
                    TmpNewStructure,
                    TmpNewElementaryType,
                ),
            ):
                # temporary operation; they will be removed
                pass
            else:
                raise SlithIRError("Not handling {} during type propagation".format(type(ir)))
    return None