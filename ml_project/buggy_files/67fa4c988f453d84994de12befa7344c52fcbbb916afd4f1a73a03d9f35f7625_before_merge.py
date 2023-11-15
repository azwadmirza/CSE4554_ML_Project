    def run(self, *tileables, **kw):
        with self.context:
            if self._executor is None:
                raise RuntimeError('Session has closed')
            dest_gpu = all(tileable.op.gpu for tileable in tileables)
            if dest_gpu:
                self._executor._engine = 'cupy'
            else:
                self._executor._engine = None
            if 'n_parallel' not in kw:
                if dest_gpu:
                    # GPU
                    cnt = cuda_count() if cuda_count is not None else 0
                    if cnt == 0:
                        raise RuntimeError('No GPU found for execution. '
                                           'Make sure NVML library is in your library path.')
                    kw['n_parallel'] = cnt
                else:
                    # CPU
                    kw['n_parallel'] = cpu_count()
            # set number of running cores
            self.context.set_ncores(kw['n_parallel'])
            res = self._executor.execute_tileables(tileables, **kw)
            return res