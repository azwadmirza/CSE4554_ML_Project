    def _resolve(self, typ, attr):
        if self._attr != attr:
            return None
        fnty = self._get_function_type(self.context, typ)
        sig = self._get_signature(self.context, fnty, (typ,), {})
        # There should only be one template
        for template in fnty.templates:
            self._inline_overloads.update(template._inline_overloads)
        return sig.return_type