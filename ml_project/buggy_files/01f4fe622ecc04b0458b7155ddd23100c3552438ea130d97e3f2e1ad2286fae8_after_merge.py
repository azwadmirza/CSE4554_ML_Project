    def overload_call_target(self, arg_types: List[Type], arg_kinds: List[int],
                             arg_names: List[str],
                             overload: Overloaded, context: Context,
                             messages: MessageBuilder = None) -> Type:
        """Infer the correct overload item to call with given argument types.

        The return value may be CallableType or AnyType (if an unique item
        could not be determined).
        """
        messages = messages or self.msg
        # TODO: For overlapping signatures we should try to get a more precise
        #       result than 'Any'.
        match = []  # type: List[CallableType]
        best_match = 0
        for typ in overload.items():
            similarity = self.erased_signature_similarity(arg_types, arg_kinds, arg_names,
                                                          typ, context=context)
            if similarity > 0 and similarity >= best_match:
                if (match and not is_same_type(match[-1].ret_type,
                                               typ.ret_type) and
                    not mypy.checker.is_more_precise_signature(
                        match[-1], typ)):
                    # Ambiguous return type. Either the function overload is
                    # overlapping (which we don't handle very well here) or the
                    # caller has provided some Any argument types; in either
                    # case we'll fall back to Any. It's okay to use Any types
                    # in calls.
                    #
                    # Overlapping overload items are generally fine if the
                    # overlapping is only possible when there is multiple
                    # inheritance, as this is rare. See docstring of
                    # mypy.meet.is_overlapping_types for more about this.
                    #
                    # Note that there is no ambiguity if the items are
                    # covariant in both argument types and return types with
                    # respect to type precision. We'll pick the best/closest
                    # match.
                    #
                    # TODO: Consider returning a union type instead if the
                    #       overlapping is NOT due to Any types?
                    return AnyType()
                else:
                    match.append(typ)
                best_match = max(best_match, similarity)
        if not match:
            messages.no_variant_matches_arguments(overload, arg_types, context)
            return AnyType()
        else:
            if len(match) == 1:
                return match[0]
            else:
                # More than one signature matches. Pick the first *non-erased*
                # matching signature, or default to the first one if none
                # match.
                for m in match:
                    if self.match_signature_types(arg_types, arg_kinds, arg_names, m,
                                                  context=context):
                        return m
                return match[0]