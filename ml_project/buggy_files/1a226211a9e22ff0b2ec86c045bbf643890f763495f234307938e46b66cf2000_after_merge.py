    def _specialize_function_args(self, args, fused_to_specific):
        for arg in args:
            if arg.type.is_fused:
                arg.type = arg.type.specialize(fused_to_specific)
                if arg.type.is_memoryviewslice:
                    arg.type.validate_memslice_dtype(arg.pos)
                if arg.annotation:
                    # TODO might be nice if annotations were specialized instead?
                    # (Or might be hard to do reliably)
                    arg.annotation.untyped = True