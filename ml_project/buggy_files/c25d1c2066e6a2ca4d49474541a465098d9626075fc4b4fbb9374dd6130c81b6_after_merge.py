    def check_argument_count(self, callee: CallableType, actual_types: List[Type],
                             actual_kinds: List[int], actual_names: List[str],
                             formal_to_actual: List[List[int]],
                             context: Context) -> None:
        """Check that the number of arguments to a function are valid.

        Also check that there are no duplicate values for arguments.
        """
        formal_kinds = callee.arg_kinds

        # Collect list of all actual arguments matched to formal arguments.
        all_actuals = []  # type: List[int]
        for actuals in formal_to_actual:
            all_actuals.extend(actuals)

        is_error = False  # Keep track of errors to avoid duplicate errors.
        for i, kind in enumerate(actual_kinds):
            if i not in all_actuals and (
                    kind != nodes.ARG_STAR or
                    not is_empty_tuple(actual_types[i])):
                # Extra actual: not matched by a formal argument.
                if kind != nodes.ARG_NAMED:
                    self.msg.too_many_arguments(callee, context)
                else:
                    self.msg.unexpected_keyword_argument(
                        callee, actual_names[i], context)
                    is_error = True
            elif kind == nodes.ARG_STAR and (
                    nodes.ARG_STAR not in formal_kinds):
                actual_type = actual_types[i]
                if isinstance(actual_type, TupleType):
                    if all_actuals.count(i) < len(actual_type.items):
                        # Too many tuple items as some did not match.
                        self.msg.too_many_arguments(callee, context)
                # *args can be applied even if the function takes a fixed
                # number of positional arguments. This may succeed at runtime.

        for i, kind in enumerate(formal_kinds):
            if kind == nodes.ARG_POS and (not formal_to_actual[i] and
                                          not is_error):
                # No actual for a mandatory positional formal.
                self.msg.too_few_arguments(callee, context, actual_names)
            elif kind in [nodes.ARG_POS, nodes.ARG_OPT,
                          nodes.ARG_NAMED] and is_duplicate_mapping(
                    formal_to_actual[i], actual_kinds):
                if (self.chk.typing_mode_full() or
                        isinstance(actual_types[formal_to_actual[i][0]], TupleType)):
                    self.msg.duplicate_argument_value(callee, i, context)
            elif (kind == nodes.ARG_NAMED and formal_to_actual[i] and
                  actual_kinds[formal_to_actual[i][0]] != nodes.ARG_NAMED):
                # Positional argument when expecting a keyword argument.
                self.msg.too_many_positional_arguments(callee, context)