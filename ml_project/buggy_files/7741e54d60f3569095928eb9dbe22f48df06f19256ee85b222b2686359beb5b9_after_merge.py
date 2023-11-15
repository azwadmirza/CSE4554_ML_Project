    def tile(cls, op):
        if get_fs(op.path, op.storage_options).isdir(op.path):
            return cls._tile_partitioned(op)
        else:
            return cls._tile_no_partitioned(op)