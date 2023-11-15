    def tile(cls, op):
        if isinstance(op.input, dict):
            return cls._tile_input_1d_tileables(op)
        elif op.input is not None:
            return cls._tile_input_tensor(op)
        else:
            return cls._tile_tensor_none(op)