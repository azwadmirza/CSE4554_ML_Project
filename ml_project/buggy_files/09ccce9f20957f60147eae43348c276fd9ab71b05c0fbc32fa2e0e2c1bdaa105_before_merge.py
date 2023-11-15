    def fetch(self, *tensors, **kw):
        ret_list = False
        if len(tensors) == 1 and isinstance(tensors[0], (tuple, list)):
            ret_list = True
            tensors = tensors[0]
        elif len(tensors) > 1:
            ret_list = True

        result = self._sess.fetch(*tensors, **kw)

        ret = []
        for r, t in zip(result, tensors):
            if t.isscalar() and hasattr(r, 'item'):
                ret.append(np.asscalar(r))
            else:
                ret.append(r)
        if ret_list:
            return ret
        return ret[0]