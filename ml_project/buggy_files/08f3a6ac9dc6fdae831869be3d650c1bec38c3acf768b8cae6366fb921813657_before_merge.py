    def run(self, *tensors, **kw):
        from . import tensor as mt

        ret_list = False
        if len(tensors) == 1 and isinstance(tensors[0], (tuple, list)):
            ret_list = True
            tensors = tensors[0]
        elif len(tensors) > 1:
            ret_list = True

        tensors = tuple(mt.tensor(t) for t in tensors)
        result = self._sess.run(*tensors, **kw)
        self._executed_keys.update(t.key for t in tensors)
        for t in tensors:
            t._execute_session = self

        ret = []
        for r, t in zip(result, tensors):
            if r is None:
                ret.append(r)
                continue
            if t.isscalar() and hasattr(r, 'item'):
                ret.append(np.asscalar(r))
            else:
                ret.append(r)
        if ret_list:
            return ret
        return ret[0]