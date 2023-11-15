    def match_signature_types(self, arg_types: List[Type], arg_kinds: List[int],
                              arg_names: List[str], callee: CallableType,
                              context: Context) -> bool:
        """Determine whether arguments types match the signature.

        Assume that argument counts are compatible.

        Return True if arguments match.
        """
        formal_to_actual = map_actuals_to_formals(arg_kinds,
                                                  arg_names,
                                                  callee.arg_kinds,
                                                  callee.arg_names,
                                                  lambda i: arg_types[i])
        ok = True

        def check_arg(caller_type: Type, original_caller_type: Type, caller_kind: int,
                      callee_type: Type, n: int, m: int, callee: CallableType,
                      context: Context, messages: MessageBuilder) -> None:
            nonlocal ok
            if not is_subtype(caller_type, callee_type):
                ok = False

        self.check_argument_types(arg_types, arg_kinds, callee, formal_to_actual,
                                  context=context, check_arg=check_arg)
        return ok