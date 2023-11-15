    def _wrap_compute(self, compute):
        @functools.wraps(compute)
        def wrapped_func(*args, **kwargs):
            # return cached value
            if self._computed is not None:
                return self._computed

            dist_sync_fn = self.dist_sync_fn
            if (dist_sync_fn is None
                    and torch.distributed.is_available()
                    and torch.distributed.is_initialized()):
                # User provided a bool, so we assume DDP if available
                dist_sync_fn = gather_all_tensors

            if self._to_sync and dist_sync_fn is not None:
                self._sync_dist(dist_sync_fn)

            self._computed = compute(*args, **kwargs)
            self.reset()

            return self._computed

        return wrapped_func