def extract_tmp_call(ins):
    assert isinstance(ins, TmpCall)

    if isinstance(ins.called, Variable) and isinstance(ins.called.type, FunctionType):
        call = InternalDynamicCall(ins.lvalue, ins.called, ins.called.type)
        call.call_id = ins.call_id
        return call
    if isinstance(ins.ori, Member):
        if isinstance(ins.ori.variable_left, Contract):
            st = ins.ori.variable_left.get_structure_from_name(ins.ori.variable_right)
            if st:
                op = NewStructure(st, ins.lvalue)
                op.call_id = ins.call_id
                return op
            libcall = LibraryCall(ins.ori.variable_left, ins.ori.variable_right, ins.nbr_arguments, ins.lvalue, ins.type_call)
            libcall.call_id = ins.call_id
            return libcall
        msgcall = HighLevelCall(ins.ori.variable_left, ins.ori.variable_right, ins.nbr_arguments, ins.lvalue, ins.type_call)
        msgcall.call_id = ins.call_id
        return msgcall

    if isinstance(ins.ori, TmpCall):
        r = extract_tmp_call(ins.ori)
        return r
    if isinstance(ins.called, SolidityVariableComposed):
        if str(ins.called) == 'block.blockhash':
            ins.called = SolidityFunction('blockhash(uint256)')
        elif str(ins.called) == 'this.balance':
            return SolidityCall(SolidityFunction('this.balance()'), ins.nbr_arguments, ins.lvalue, ins.type_call)

    if isinstance(ins.called, SolidityFunction):
        return SolidityCall(ins.called, ins.nbr_arguments, ins.lvalue, ins.type_call)

    if isinstance(ins.ori, TmpNewElementaryType):
        return NewElementaryType(ins.ori.type, ins.lvalue)

    if isinstance(ins.ori, TmpNewContract):
        op = NewContract(Constant(ins.ori.contract_name), ins.lvalue)
        op.call_id = ins.call_id
        return op

    if isinstance(ins.ori, TmpNewArray):
        return NewArray(ins.ori.depth, ins.ori.array_type, ins.lvalue)

    if isinstance(ins.called, Structure):
        op = NewStructure(ins.called, ins.lvalue)
        op.call_id = ins.call_id
        return op

    if isinstance(ins.called, Event):
        return EventCall(ins.called.name)


    raise Exception('Not extracted {} {}'.format(type(ins.called), ins))