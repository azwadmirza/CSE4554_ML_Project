    def __init__(self, _dict=dict, preserve=False):
        from dynaconf.vendor.toml.decoder import CommentValue
        super(TomlPreserveCommentEncoder, self).__init__(_dict, preserve)
        self.dump_funcs[CommentValue] = lambda v: v.dump(self.dump_value)