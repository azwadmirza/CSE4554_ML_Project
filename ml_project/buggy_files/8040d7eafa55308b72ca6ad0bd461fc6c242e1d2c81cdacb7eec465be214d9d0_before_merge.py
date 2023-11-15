    def tile(cls, op):
        if isinstance(op.input, dict):
            return cls._tile_input_1d_tileables(op)
        else:
            return cls._tile_input_tensor(op)