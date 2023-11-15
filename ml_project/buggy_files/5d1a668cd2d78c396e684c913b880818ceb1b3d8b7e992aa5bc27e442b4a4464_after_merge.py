    def resolve_getattr(self, typ, attr):
        """
        Resolve getting the attribute *attr* (a string) on the Numba type.
        The attribute's type is returned, or None if resolution failed.
        """
        def core(typ):
            out = self.find_matching_getattr_template(typ, attr)
            if out:
                return out['return_type']

        out = core(typ)
        if out is not None:
            return out

        # Try again without literals
        out = core(types.unliteral(typ))
        if out is not None:
            return out

        if isinstance(typ, types.Module):
            attrty = self.resolve_module_constants(typ, attr)
            if attrty is not None:
                return attrty