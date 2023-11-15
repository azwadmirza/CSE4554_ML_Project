    def resolve_getattr(self, typ, attr):
        """
        Resolve getting the attribute *attr* (a string) on the Numba type.
        The attribute's type is returned, or None if resolution failed.
        """
        def core(typ):
            for attrinfo in self._get_attribute_templates(typ):
                ret = attrinfo.resolve(typ, attr)
                if ret is not None:
                    return ret

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