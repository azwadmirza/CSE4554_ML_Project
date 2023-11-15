    def __validate_msg(line: Line, string_idx: int) -> TResult[None]:
        """Validate (M)erge (S)tring (G)roup

        Transform-time string validation logic for __merge_string_group(...).

        Returns:
            * Ok(None), if ALL validation checks (listed below) pass.
                OR
            * Err(CannotTransform), if any of the following are true:
                - The target string is not in a string group (i.e. it has no
                  adjacent strings).
                - The string group has more than one inline comment.
                - The string group has an inline comment that appears to be a pragma.
                - The set of all string prefixes in the string group is of
                  length greater than one and is not equal to {"", "f"}.
                - The string group consists of raw strings.
        """
        num_of_inline_string_comments = 0
        set_of_prefixes = set()
        num_of_strings = 0
        for leaf in line.leaves[string_idx:]:
            if leaf.type != token.STRING:
                # If the string group is trailed by a comma, we count the
                # comments trailing the comma to be one of the string group's
                # comments.
                if leaf.type == token.COMMA and id(leaf) in line.comments:
                    num_of_inline_string_comments += 1
                break

            if has_triple_quotes(leaf.value):
                return TErr("StringMerger does NOT merge multiline strings.")

            num_of_strings += 1
            prefix = get_string_prefix(leaf.value)
            if "r" in prefix:
                return TErr("StringMerger does NOT merge raw strings.")

            set_of_prefixes.add(prefix)

            if id(leaf) in line.comments:
                num_of_inline_string_comments += 1
                if contains_pragma_comment(line.comments[id(leaf)]):
                    return TErr("Cannot merge strings which have pragma comments.")

        if num_of_strings < 2:
            return TErr(
                f"Not enough strings to merge (num_of_strings={num_of_strings})."
            )

        if num_of_inline_string_comments > 1:
            return TErr(
                f"Too many inline string comments ({num_of_inline_string_comments})."
            )

        if len(set_of_prefixes) > 1 and set_of_prefixes != {"", "f"}:
            return TErr(f"Too many different prefixes ({set_of_prefixes}).")

        return Ok(None)