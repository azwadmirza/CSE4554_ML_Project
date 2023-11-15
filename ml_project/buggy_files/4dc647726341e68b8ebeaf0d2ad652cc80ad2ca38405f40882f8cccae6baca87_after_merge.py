    def _explain_ambiguous(self, *args, **kws):
        assert not kws, "kwargs not handled"
        args = tuple([self.typeof_pyval(a) for a in args])
        sigs = [cr.signature for cr in self._compileinfos.values()]
        resolve_overload(self.typingctx, self.py_func, sigs, args, kws)