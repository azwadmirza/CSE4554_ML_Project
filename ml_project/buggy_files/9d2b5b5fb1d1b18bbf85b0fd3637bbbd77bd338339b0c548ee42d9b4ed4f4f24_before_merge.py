def extract_tmp_call(ins, contract):
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