def extract_tmp_call(ins, contract):  # pylint: disable=too-many-locals
    assert isinstance(ins, TmpCall)

    if isinstance(ins.called, Variable) and isinstance(ins.called.type, FunctionType):
        # If the call is made to a variable member, where the member is this
        # We need to convert it to a HighLelelCall and not an internal dynamic call
        if isinstance(ins.ori, Member) and ins.ori.variable_left == SolidityVariable("this"):
            pass
        else:
            call = InternalDynamicCall(ins.lvalue, ins.called, ins.called.type)
            call.set_expression(ins.expression)
            call.call_id = ins.call_id
            return call
    if isinstance(ins.ori, Member):
        # If there is a call on an inherited contract, it is an internal call or an event
        if ins.ori.variable_left in contract.inheritance + [contract]:
            if str(ins.ori.variable_right) in [f.name for f in contract.functions]:
                internalcall = InternalCall(
                    (ins.ori.variable_right, ins.ori.variable_left.name),
                    ins.nbr_arguments,
                    ins.lvalue,
                    ins.type_call,
                )
                internalcall.set_expression(ins.expression)
                internalcall.call_id = ins.call_id
                return internalcall
            if str(ins.ori.variable_right) in [f.name for f in contract.events]:
                eventcall = EventCall(ins.ori.variable_right)
                eventcall.set_expression(ins.expression)
                eventcall.call_id = ins.call_id
                return eventcall
        if isinstance(ins.ori.variable_left, Contract):
            st = ins.ori.variable_left.get_structure_from_name(ins.ori.variable_right)
            if st:
                op = NewStructure(st, ins.lvalue)
                op.set_expression(ins.expression)
                op.call_id = ins.call_id
                return op
            libcall = LibraryCall(
                ins.ori.variable_left,
                ins.ori.variable_right,
                ins.nbr_arguments,
                ins.lvalue,
                ins.type_call,
            )
            libcall.set_expression(ins.expression)
            libcall.call_id = ins.call_id
            return libcall
        if isinstance(ins.ori.variable_left, Function):
            # Support for library call where the parameter is a function
            # We could merge this with the standard library handling
            # Except that we will have some troubles with using_for
            # As the type of the funciton will not match function()
            # Additionally we do not have a correct view on the parameters of the tmpcall
            # At this level
            #
            # library FunctionExtensions {
            #     function h(function() internal _t, uint8) internal {  }
            # }
            # contract FunctionMembers {
            #     using FunctionExtensions for function();
            #
            #     function f() public {
            #         f.h(1);
            #     }
            # }
            using_for = ins.node.function.contract.using_for

            targeted_libraries = (
                [] + using_for.get("*", []) + using_for.get(FunctionType([], []), [])
            )
            lib_contract: Contract
            candidates = []
            for lib_contract_type in targeted_libraries:
                if not isinstance(lib_contract_type, UserDefinedType) and isinstance(
                    lib_contract_type.type, Contract
                ):
                    continue
                lib_contract = lib_contract_type.type
                for lib_func in lib_contract.functions:
                    if lib_func.name == ins.ori.variable_right:
                        candidates.append(lib_func)

            if len(candidates) == 1:
                lib_func = candidates[0]
                lib_call = LibraryCall(
                    lib_func.contract,
                    Constant(lib_func.name),
                    len(lib_func.parameters),
                    ins.lvalue,
                    "d",
                )
                lib_call.set_expression(ins.expression)
                lib_call.set_node(ins.node)
                lib_call.call_gas = ins.call_gas
                lib_call.call_id = ins.call_id
                lib_call.set_node(ins.node)
                lib_call.function = lib_func
                lib_call.arguments.append(ins.ori.variable_left)
                return lib_call
            # We do not support something lik
            # library FunctionExtensions {
            #     function h(function() internal _t, uint8) internal {  }
            #     function h(function() internal _t, bool) internal {  }
            # }
            # contract FunctionMembers {
            #     using FunctionExtensions for function();
            #
            #     function f() public {
            #         f.h(1);
            #     }
            # }
            to_log = "Slither does not support dynamic functions to libraries if functions have the same name"
            to_log += f"{[candidate.full_name for candidate in candidates]}"
            raise SlithIRError(to_log)
        msgcall = HighLevelCall(
            ins.ori.variable_left,
            ins.ori.variable_right,
            ins.nbr_arguments,
            ins.lvalue,
            ins.type_call,
        )
        msgcall.call_id = ins.call_id

        if ins.call_gas:
            msgcall.call_gas = ins.call_gas
        if ins.call_value:
            msgcall.call_value = ins.call_value
        msgcall.set_expression(ins.expression)

        return msgcall

    if isinstance(ins.ori, TmpCall):
        r = extract_tmp_call(ins.ori, contract)
        r.set_node(ins.node)
        return r
    if isinstance(ins.called, SolidityVariableComposed):
        if str(ins.called) == "block.blockhash":
            ins.called = SolidityFunction("blockhash(uint256)")
        elif str(ins.called) == "this.balance":
            s = SolidityCall(
                SolidityFunction("this.balance()"),
                ins.nbr_arguments,
                ins.lvalue,
                ins.type_call,
            )
            s.set_expression(ins.expression)
            return s

    if isinstance(ins.called, SolidityFunction):
        s = SolidityCall(ins.called, ins.nbr_arguments, ins.lvalue, ins.type_call)
        s.set_expression(ins.expression)
        return s

    if isinstance(ins.ori, TmpNewElementaryType):
        n = NewElementaryType(ins.ori.type, ins.lvalue)
        n.set_expression(ins.expression)
        return n

    if isinstance(ins.ori, TmpNewContract):
        op = NewContract(Constant(ins.ori.contract_name), ins.lvalue)
        op.set_expression(ins.expression)
        op.call_id = ins.call_id
        if ins.call_value:
            op.call_value = ins.call_value
        if ins.call_salt:
            op.call_salt = ins.call_salt
        return op

    if isinstance(ins.ori, TmpNewArray):
        n = NewArray(ins.ori.depth, ins.ori.array_type, ins.lvalue)
        n.set_expression(ins.expression)
        return n

    if isinstance(ins.called, Structure):
        op = NewStructure(ins.called, ins.lvalue)
        op.set_expression(ins.expression)
        op.call_id = ins.call_id
        op.set_expression(ins.expression)
        return op

    if isinstance(ins.called, Event):
        e = EventCall(ins.called.name)
        e.set_expression(ins.expression)
        return e

    if isinstance(ins.called, Contract):
        # Called a base constructor, where there is no constructor
        if ins.called.constructor is None:
            return Nop()
        # Case where:
        # contract A{ constructor(uint) }
        # contract B is A {}
        # contract C is B{ constructor() A(10) B() {}
        # C calls B(), which does not exist
        # Ideally we should compare here for the parameters types too
        if len(ins.called.constructor.parameters) != ins.nbr_arguments:
            return Nop()
        internalcall = InternalCall(
            ins.called.constructor, ins.nbr_arguments, ins.lvalue, ins.type_call
        )
        internalcall.call_id = ins.call_id
        internalcall.set_expression(ins.expression)
        return internalcall

    raise Exception("Not extracted {} {}".format(type(ins.called), ins))