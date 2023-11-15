    def tile(cls, op):
        # make sure all tensor have known chunk shapes
        check_chunks_unknown_shape(op.inputs, TilesError)

        if isinstance(op.input, dict):
            return cls._tile_input_1d_tileables(op)
        else:
            return cls._tile_input_tensor(op)