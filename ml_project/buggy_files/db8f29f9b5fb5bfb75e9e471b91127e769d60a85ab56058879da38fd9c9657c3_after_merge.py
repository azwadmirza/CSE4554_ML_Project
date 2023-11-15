def propagate_type_and_convert_call(result, node):
    """
    Propagate the types variables and convert tmp call to real call operation
    """
    calls_value = {}
    calls_gas = {}

    call_data = []

    idx = 0
    # use of while len() as result can be modified during the iteration
    while idx < len(result):
        ins = result[idx]

        if isinstance(ins, TmpCall):
            new_ins = extract_tmp_call(ins, node.function.contract)
            if new_ins:
                new_ins.set_node(ins.node)
                ins = new_ins
                result[idx] = ins

        if isinstance(ins, Argument):
            if ins.get_type() in [ArgumentType.GAS]:
                assert not ins.call_id in calls_gas
                calls_gas[ins.call_id] = ins.argument
            elif ins.get_type() in [ArgumentType.VALUE]:
                assert not ins.call_id in calls_value
                calls_value[ins.call_id] = ins.argument
            else:
                assert ins.get_type() == ArgumentType.CALL
                call_data.append(ins.argument)

        if isinstance(ins, (HighLevelCall, NewContract, InternalDynamicCall)):
            if ins.call_id in calls_value:
                ins.call_value = calls_value[ins.call_id]
            if ins.call_id in calls_gas:
                ins.call_gas = calls_gas[ins.call_id]

        if isinstance(ins, (Call, NewContract, NewStructure)):
            # We might have stored some arguments for libraries
            if ins.arguments:
                call_data = ins.arguments + call_data
            ins.arguments = call_data
            call_data = []

        if is_temporary(ins):
            del result[idx]
            continue

        new_ins = propagate_types(ins, node)
        if new_ins:
            if isinstance(new_ins, (list,)):
                if len(new_ins) == 2:
                    new_ins[0].set_node(ins.node)
                    new_ins[1].set_node(ins.node)
                    del result[idx]
                    result.insert(idx, new_ins[0])
                    result.insert(idx + 1, new_ins[1])
                    idx = idx + 1
                elif len(new_ins) == 3:
                    new_ins[0].set_node(ins.node)
                    new_ins[1].set_node(ins.node)
                    new_ins[2].set_node(ins.node)
                    del result[idx]
                    result.insert(idx, new_ins[0])
                    result.insert(idx + 1, new_ins[1])
                    result.insert(idx + 2, new_ins[2])
                    idx = idx + 2
                else:
                    # Pop conversion
                    assert len(new_ins) == 6
                    new_ins[0].set_node(ins.node)
                    new_ins[1].set_node(ins.node)
                    new_ins[2].set_node(ins.node)
                    new_ins[3].set_node(ins.node)
                    new_ins[4].set_node(ins.node)
                    new_ins[5].set_node(ins.node)
                    del result[idx]
                    result.insert(idx, new_ins[0])
                    result.insert(idx + 1, new_ins[1])
                    result.insert(idx + 2, new_ins[2])
                    result.insert(idx + 3, new_ins[3])
                    result.insert(idx + 4, new_ins[4])
                    result.insert(idx + 5, new_ins[5])
                    idx = idx + 5
            else:
                new_ins.set_node(ins.node)
                result[idx] = new_ins
        idx = idx + 1
    return result