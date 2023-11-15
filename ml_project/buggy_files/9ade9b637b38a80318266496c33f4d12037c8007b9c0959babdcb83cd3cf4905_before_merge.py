def lower_parfor_sequential(func_ir, typemap, calltypes):
    parfor_found = False
    new_blocks = {}
    for (block_label, block) in func_ir.blocks.items():
        scope = block.scope
        i = _find_first_parfor(block.body)
        while i!=-1:
            parfor_found = True
            inst = block.body[i]
            loc = inst.init_block.loc
            # split block across parfor
            prev_block = ir.Block(scope, loc)
            prev_block.body = block.body[:i]
            block.body = block.body[i+1:]
            # previous block jump to parfor init block
            init_label = next_label()
            prev_block.body.append(ir.Jump(init_label, loc))
            new_blocks[init_label] = inst.init_block
            new_blocks[block_label] = prev_block
            block_label = next_label()

            ndims = len(inst.loop_nests)
            for i in range(ndims):
                loopnest = inst.loop_nests[i]
                # create range block for loop
                range_label = next_label()
                header_label = next_label()
                range_block = mk_range_block(typemap, loopnest.start,
                    loopnest.stop, loopnest.step, calltypes, scope, loc)
                range_block.body[-1].target = header_label # fix jump target
                phi_var = range_block.body[-2].target
                new_blocks[range_label] = range_block
                header_block = mk_loop_header(typemap, phi_var, calltypes,
                    scope, loc)
                header_block.body[-2].target = loopnest.index_variable
                new_blocks[header_label] = header_block
                # jump to this new inner loop
                if i==0:
                    inst.init_block.body.append(ir.Jump(range_label, loc))
                    header_block.body[-1].falsebr = block_label
                else:
                    new_blocks[prev_header_label].body[-1].truebr = range_label
                    header_block.body[-1].falsebr = prev_header_label
                prev_header_label = header_label # to set truebr next loop

            # last body block jump to inner most header
            body_last_label = max(inst.loop_body.keys())
            inst.loop_body[body_last_label].body.append(
                ir.Jump(header_label, loc))
            # inner most header jumps to first body block
            body_first_label = min(inst.loop_body.keys())
            header_block.body[-1].truebr = body_first_label
            # add parfor body to blocks
            for (l, b) in inst.loop_body.items():
                new_blocks[l] = b
            i = _find_first_parfor(block.body)

        # old block stays either way
        new_blocks[block_label] = block
    func_ir.blocks = new_blocks
    # rename only if parfor found and replaced (avoid test_flow_control error)
    if parfor_found:
        func_ir.blocks = rename_labels(func_ir.blocks)
    dprint_func_ir(func_ir, "after parfor sequential lowering")
    return