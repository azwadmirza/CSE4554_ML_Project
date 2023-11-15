    def seq(self, *args):
        # type: (Any) -> Any
        if 'rt' in self.typ:
            from ruamel.yaml.comments import CommentedSeq

            return CommentedSeq(*args)
        else:
            return list(*args)