    def fetch(self, *tileables, **kw):
        ret_list = False
        if len(tileables) == 1 and isinstance(tileables[0], (tuple, list)):
            ret_list = True
            tileables = tileables[0]
        elif len(tileables) > 1:
            ret_list = True

        result = self._sess.fetch(*tileables, **kw)

        ret = []
        for r, t in zip(result, tileables):
            if hasattr(t, 'isscalar') and t.isscalar() and getattr(r, 'size', None) == 1:
                ret.append(r.item())
            else:
                ret.append(r)
        if ret_list:
            return ret
        return ret[0]