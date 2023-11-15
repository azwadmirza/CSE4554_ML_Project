        def debug_print(pass_name, print_condition, printable_condition):
            if pass_name in print_condition:
                fid = internal_state.func_id
                args = (fid.modname, fid.func_qualname, self.pipeline_name,
                        printable_condition, pass_name)
                print(("%s.%s: %s: %s %s" % args).center(120, '-'))
                if internal_state.func_ir is not None:
                    internal_state.func_ir.dump()
                else:
                    print("func_ir is None")