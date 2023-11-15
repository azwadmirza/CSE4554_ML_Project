    def _simplify(self, seen=None):
        """
        Simplify a promotion type tree:

            promote(int_, float_)
                -> float_

            promote(deferred(x), promote(float_, double), int_, promote(<self>))
                -> promote(deferred(x), double)

            promote(deferred(x), deferred(y))
                -> promote(deferred(x), deferred(y))
        """
        if seen is None:
            seen = set()

        # Find all types in the type graph and eliminate nested promotion types
        types = self.find_types(seen)
        # types = self.find_simple(seen)

        resolved_types = [type for type in types if not type.is_unresolved]
        unresolved_types = [type for type in types if type.is_unresolved]
        self.get_partial_types(unresolved_types)

        self.variable.type = self
        if not resolved_types:
            # Everything is deferred
            self.resolved_type = None
            return False
        else:
            # Simplify as much as possible
            if self.assignment:
                result_type, unresolved_types = promote_for_assignment(
                        self.context, resolved_types, unresolved_types,
                        self.variable.name)
            else:
                result_type = promote_for_arithmetic(self.context, resolved_types)

            self.resolved_type = result_type
            if len(resolved_types) == len(types) or not unresolved_types:
                self.variable.type = result_type
                return True
            else:
                old_types = self.types
                self.types = set([result_type] + unresolved_types)
                return old_types != self.types