    def check_argument_types(self, arg_types: List[Type], arg_kinds: List[int],
                             callee: CallableType,
                             formal_to_actual: List[List[int]],
                             context: Context,
                             messages: MessageBuilder = None,
                             check_arg: ArgChecker = None) -> None:
        """Check argument types against a callable type.

        Report errors if the argument types are not compatible.
        """
        messages = messages or self.msg
        check_arg = check_arg or self.check_arg
        # Keep track of consumed tuple *arg items.
        tuple_counter = [0]
        for i, actuals in enumerate(formal_to_actual):
            for actual in actuals:
                arg_type = arg_types[actual]
                # Check that a *arg is valid as varargs.
                if (arg_kinds[actual] == nodes.ARG_STAR and
                        not self.is_valid_var_arg(arg_type)):
                    messages.invalid_var_arg(arg_type, context)
                if (arg_kinds[actual] == nodes.ARG_STAR2 and
                        not self.is_valid_keyword_var_arg(arg_type)):
                    messages.invalid_keyword_var_arg(arg_type, context)
                # Get the type of an individual actual argument (for *args
                # and **args this is the item type, not the collection type).
                actual_type = get_actual_type(arg_type, arg_kinds[actual],
                                              tuple_counter)
                check_arg(actual_type, arg_type, arg_kinds[actual],
                          callee.arg_types[i],
                          actual + 1, i + 1, callee, context, messages)

                # There may be some remaining tuple varargs items that haven't
                # been checked yet. Handle them.
                if (callee.arg_kinds[i] == nodes.ARG_STAR and
                        arg_kinds[actual] == nodes.ARG_STAR and
                        isinstance(arg_types[actual], TupleType)):
                    tuplet = cast(TupleType, arg_types[actual])
                    while tuple_counter[0] < len(tuplet.items):
                        actual_type = get_actual_type(arg_type,
                                                      arg_kinds[actual],
                                                      tuple_counter)
                        check_arg(actual_type, arg_type, arg_kinds[actual],
                                  callee.arg_types[i],
                                  actual + 1, i + 1, callee, context, messages)