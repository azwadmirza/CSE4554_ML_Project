    def unify_pairs(self, first, second):
        """
        Try to unify the two given types.  A third type is returned,
        or pyobject in case of failure.
        """
        if first == second:
            return first
        
        if first is types.undefined:
            return second
        elif second is types.undefined:
            return first

        # Types with special unification rules
        unified = first.unify(self, second)
        if unified is not None:
            return unified

        unified = second.unify(self, first)
        if unified is not None:
            return unified

        # Other types with simple conversion rules
        conv = self.can_convert(fromty=first, toty=second)
        if conv is not None and conv <= Conversion.safe:
            # Can convert from first to second
            return second

        conv = self.can_convert(fromty=second, toty=first)
        if conv is not None and conv <= Conversion.safe:
            # Can convert from second to first
            return first

        # Cannot unify
        return types.pyobject