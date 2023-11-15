    def do_transform(self, line: Line, string_idx: int) -> Iterator[TResult[Line]]:
        LL = line.leaves

        string_parser = StringParser()
        rpar_idx = string_parser.parse(LL, string_idx)

        for leaf in (LL[string_idx - 1], LL[rpar_idx]):
            if line.comments_after(leaf):
                yield TErr(
                    "Will not strip parentheses which have comments attached to them."
                )

        new_line = line.clone()
        new_line.comments = line.comments.copy()
        append_leaves(new_line, line, LL[: string_idx - 1])

        string_leaf = Leaf(token.STRING, LL[string_idx].value)
        LL[string_idx - 1].remove()
        replace_child(LL[string_idx], string_leaf)
        new_line.append(string_leaf)

        append_leaves(
            new_line, line, LL[string_idx + 1 : rpar_idx] + LL[rpar_idx + 1 :]
        )

        LL[rpar_idx].remove()

        yield Ok(new_line)