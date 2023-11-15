    def tile(cls, op):
        if os.path.isdir(op.path):
            return cls._tile_partitioned(op)
        else:
            return cls._tile_no_partitioned(op)