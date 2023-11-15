    def build_cfg (cls, code_obj, *args, **kws):
        ret_val = cls(*args, **kws)
        opmap = opcode.opname
        ret_val.crnt_block = 0
        ret_val.code_len = len(code_obj.co_code)
        ret_val.add_block(0)
        ret_val.blocks_writes[0] = set(range(code_obj.co_argcount))
        last_was_jump = True # At start there is no prior basic block
                             # to link up with, so skip building a
                             # fallthrough edge.
        for i, op, arg in itercode(code_obj.co_code):
            if i in ret_val.blocks:
                if not last_was_jump:
                    ret_val.add_edge(ret_val.crnt_block, i)
                ret_val.crnt_block = i
            last_was_jump = False
            method_name = "op_" + opmap[op]
            if hasattr(ret_val, method_name):
                last_was_jump = getattr(ret_val, method_name)(i, op, arg)
        ret_val.unlink_unreachables()
        del ret_val.crnt_block, ret_val.code_len
        return ret_val