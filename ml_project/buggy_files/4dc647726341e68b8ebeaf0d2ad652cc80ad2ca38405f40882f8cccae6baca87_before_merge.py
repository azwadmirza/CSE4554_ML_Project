    def _explain_ambiguous(self, *args, **kws):
        assert not kws, "kwargs not handled"
        args = tuple([self.typeof_pyval(a) for a in args])
        resolve_overload(self.typingctx, self.py_func,
                         tuple(self.overloads.keys()), args, kws)