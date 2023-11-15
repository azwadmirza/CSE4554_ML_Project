        def typer(ref, deg = False):
            if isinstance(ref, types.Array):
                return ref.copy(dtype=ref.underlying_float)
            else:
                return types.float64