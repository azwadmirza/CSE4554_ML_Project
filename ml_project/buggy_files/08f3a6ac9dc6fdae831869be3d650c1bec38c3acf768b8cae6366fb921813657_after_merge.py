    def run(self, *tensors, **kw):
        from . import tensor as mt

        ret_list = False
        if len(tensors) == 1 and isinstance(tensors[0], (tuple, list)):
            ret_list = True
            tensors = tensors[0]
        elif len(tensors) > 1:
            ret_list = True

        tensors = tuple(mt.tensor(t) for t in tensors)
        run_tensors = []
        fetch_results = dict()

        # those executed tensors should fetch data directly, submit the others
        for t in tensors:
            if t.key in self._executed_keys:
                fetch_results[t.key] = self.fetch(t)
            else:
                run_tensors.append(t)
        if all([t.key in fetch_results for t in tensors]):
            results = [fetch_results[t.key] for t in tensors]
            return results if ret_list else results[0]

        result = self._sess.run(*run_tensors, **kw)
        self._executed_keys.update(t.key for t in run_tensors)
        for t in run_tensors:
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

        results = []
        result_iter = iter(ret)
        for k in [t.key for t in tensors]:
            if k in fetch_results:
                results.append(fetch_results[k])
            else:
                results.append(next(result_iter))
        if ret_list:
            return results
        return results[0]