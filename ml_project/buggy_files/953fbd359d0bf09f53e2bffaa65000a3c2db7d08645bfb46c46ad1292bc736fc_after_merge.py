    def seq(self, *args):
        # type: (Any) -> Any
        if 'rt' in self.typ:
            from dynaconf.vendor.ruamel.yaml.comments import CommentedSeq

            return CommentedSeq(*args)
        else:
            return list(*args)