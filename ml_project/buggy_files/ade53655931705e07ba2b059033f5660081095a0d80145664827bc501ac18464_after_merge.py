    def map(self, **kw):
        # type: (Any) -> Any
        if 'rt' in self.typ:
            from dynaconf.vendor.ruamel.yaml.comments import CommentedMap

            return CommentedMap(**kw)
        else:
            return dict(**kw)