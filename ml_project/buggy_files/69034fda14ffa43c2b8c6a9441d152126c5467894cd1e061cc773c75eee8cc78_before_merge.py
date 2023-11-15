def generate_ssa_irs(node, local_variables_instances, all_local_variables_instances, state_variables_instances, all_state_variables_instances, init_local_variables_instances, visited):

    if node in visited:
        return

    if node.type in [NodeType.ENDIF, NodeType.ENDLOOP] and any(not father in visited for father in node.fathers):
        return

    # visited is shared
    visited.append(node)

    for ir in node.irs_ssa:
        assert isinstance(ir, Phi)
        update_lvalue(ir, node, local_variables_instances, all_local_variables_instances, state_variables_instances, all_state_variables_instances)


    # these variables are lived only during the liveness of the block
    # They dont need phi function
    temporary_variables_instances = dict()
    reference_variables_instances = dict()

    for ir in node.irs:
        new_ir = copy_ir(ir,
                         local_variables_instances,
                         state_variables_instances,
                         temporary_variables_instances,
                         reference_variables_instances,
                         all_local_variables_instances)

        update_lvalue(new_ir,
                      node,
                      local_variables_instances,
                      all_local_variables_instances,
                      state_variables_instances,
                      all_state_variables_instances)

        if new_ir:

            node.add_ssa_ir(new_ir)

            if isinstance(ir, (InternalCall, HighLevelCall, InternalDynamicCall, LowLevelCall)):
                if isinstance(ir, LibraryCall):
                    continue
                for variable in all_state_variables_instances.values():
                    if not is_used_later(node, variable):
                        continue
                    new_var = StateIRVariable(variable)
                    new_var.index = all_state_variables_instances[variable.canonical_name].index + 1
                    all_state_variables_instances[variable.canonical_name] = new_var
                    state_variables_instances[variable.canonical_name] = new_var
                    phi_ir = PhiCallback(new_var, {node}, new_ir, variable)
                    # rvalues are fixed in solc_parsing.declaration.function
                    node.add_ssa_ir(phi_ir)

            if isinstance(new_ir, (Assignment, Binary)):
                if isinstance(new_ir.lvalue, LocalIRVariable):
                    if new_ir.lvalue.is_storage:
                        if isinstance(new_ir.rvalue, ReferenceVariable):
                            refers_to = new_ir.rvalue.points_to_origin
                            new_ir.lvalue.add_refers_to(refers_to)
                        else:
                            new_ir.lvalue.add_refers_to(new_ir.rvalue)


    for succ in node.dominator_successors:
        generate_ssa_irs(succ,
                         dict(local_variables_instances),
                         all_local_variables_instances,
                         dict(state_variables_instances),
                         all_state_variables_instances,
                         init_local_variables_instances,
                         visited)

    for dominated in node.dominance_frontier:
        generate_ssa_irs(dominated,
                         dict(local_variables_instances),
                         all_local_variables_instances,
                         dict(state_variables_instances),
                         all_state_variables_instances,
                         init_local_variables_instances,
                         visited)