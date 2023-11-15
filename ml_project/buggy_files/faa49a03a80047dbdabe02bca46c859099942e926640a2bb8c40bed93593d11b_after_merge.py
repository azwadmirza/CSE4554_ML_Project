    def erased_signature_similarity(self, arg_types: List[Type], arg_kinds: List[int],
                                    arg_names: List[str], callee: CallableType,
                                    context: Context) -> int:
        """Determine whether arguments could match the signature at runtime.

        Return similarity level (0 = no match, 1 = can match, 2 = non-promotion match). See
        overload_arg_similarity for a discussion of similarity levels.
        """
        formal_to_actual = map_actuals_to_formals(arg_kinds,
                                                  arg_names,
                                                  callee.arg_kinds,
                                                  callee.arg_names,
                                                  lambda i: arg_types[i])

        if not self.check_argument_count(callee, arg_types, arg_kinds, arg_names,
                                         formal_to_actual, None, None):
            # Too few or many arguments -> no match.
            return 0

        similarity = 2

        def check_arg(caller_type: Type, original_caller_type: Type, caller_kind: int,
                      callee_type: Type, n: int, m: int, callee: CallableType,
                      context: Context, messages: MessageBuilder) -> None:
            nonlocal similarity
            similarity = min(similarity,
                             overload_arg_similarity(caller_type, callee_type))
            if similarity == 0:
                # No match -- exit early since none of the remaining work can change
                # the result.
                raise Finished

        try:
            self.check_argument_types(arg_types, arg_kinds, callee, formal_to_actual,
                                      context=context, check_arg=check_arg)
        except Finished:
            pass

        return similarity