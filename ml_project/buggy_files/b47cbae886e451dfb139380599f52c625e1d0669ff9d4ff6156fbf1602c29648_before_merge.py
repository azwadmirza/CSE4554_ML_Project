    def yaml_set_comment_before_after_key(
        self, key, before=None, indent=0, after=None, after_indent=None
    ):
        # type: (Any, Any, Any, Any, Any) -> None
        """
        expects comment (before/after) to be without `#` and possible have multiple lines
        """
        from ruamel.yaml.error import CommentMark
        from ruamel.yaml.tokens import CommentToken

        def comment_token(s, mark):
            # type: (Any, Any) -> Any
            # handle empty lines as having no comment
            return CommentToken(('# ' if s else "") + s + '\n', mark, None)

        if after_indent is None:
            after_indent = indent + 2
        if before and (len(before) > 1) and before[-1] == '\n':
            before = before[:-1]  # strip final newline if there
        if after and after[-1] == '\n':
            after = after[:-1]  # strip final newline if there
        start_mark = CommentMark(indent)
        c = self.ca.items.setdefault(key, [None, [], None, None])
        if before == '\n':
            c[1].append(comment_token("", start_mark))
        elif before:
            for com in before.split('\n'):
                c[1].append(comment_token(com, start_mark))
        if after:
            start_mark = CommentMark(after_indent)
            if c[3] is None:
                c[3] = []
            for com in after.split('\n'):
                c[3].append(comment_token(com, start_mark))  # type: ignore