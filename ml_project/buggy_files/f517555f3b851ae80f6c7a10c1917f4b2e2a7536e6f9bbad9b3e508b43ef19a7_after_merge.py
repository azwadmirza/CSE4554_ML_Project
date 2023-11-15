    def visit_overloaded(self, left: Overloaded) -> bool:
        right = self.right
        if isinstance(right, Instance):
            if right.type.is_protocol and right.type.protocol_members == ['__call__']:
                # same as for CallableType
                call = find_member('__call__', right, left, is_operator=True)
                assert call is not None
                if self._is_subtype(left, call):
                    return True
            return self._is_subtype(left.fallback, right)
        elif isinstance(right, CallableType):
            for item in left.items():
                if self._is_subtype(item, right):
                    return True
            return False
        elif isinstance(right, Overloaded):
            # Ensure each overload in the right side (the supertype) is accounted for.
            previous_match_left_index = -1
            matched_overloads = set()
            possible_invalid_overloads = set()

            for right_index, right_item in enumerate(right.items()):
                found_match = False

                for left_index, left_item in enumerate(left.items()):
                    subtype_match = self._is_subtype(left_item, right_item)\

                    # Order matters: we need to make sure that the index of
                    # this item is at least the index of the previous one.
                    if subtype_match and previous_match_left_index <= left_index:
                        if not found_match:
                            # Update the index of the previous match.
                            previous_match_left_index = left_index
                            found_match = True
                            matched_overloads.add(left_item)
                            possible_invalid_overloads.discard(left_item)
                    else:
                        # If this one overlaps with the supertype in any way, but it wasn't
                        # an exact match, then it's a potential error.
                        if (is_callable_compatible(left_item, right_item,
                                    is_compat=self._is_subtype, ignore_return=True,
                                    ignore_pos_arg_names=self.ignore_pos_arg_names) or
                                is_callable_compatible(right_item, left_item,
                                        is_compat=self._is_subtype, ignore_return=True,
                                        ignore_pos_arg_names=self.ignore_pos_arg_names)):
                            # If this is an overload that's already been matched, there's no
                            # problem.
                            if left_item not in matched_overloads:
                                possible_invalid_overloads.add(left_item)

                if not found_match:
                    return False

            if possible_invalid_overloads:
                # There were potentially invalid overloads that were never matched to the
                # supertype.
                return False
            return True
        elif isinstance(right, UnboundType):
            return True
        elif isinstance(right, TypeType):
            # All the items must have the same type object status, so
            # it's sufficient to query only (any) one of them.
            # This is unsound, we don't check all the __init__ signatures.
            return left.is_type_obj() and self._is_subtype(left.items()[0], right)
        else:
            return False