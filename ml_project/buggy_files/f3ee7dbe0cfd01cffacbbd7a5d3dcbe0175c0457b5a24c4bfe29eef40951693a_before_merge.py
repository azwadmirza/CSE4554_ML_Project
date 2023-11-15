    def unify_pairs(self, first, second):
        """
        Try to unify the two given types.  A third type is returned,
        or None in case of failure.
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
            return conv

        return types.pyobject