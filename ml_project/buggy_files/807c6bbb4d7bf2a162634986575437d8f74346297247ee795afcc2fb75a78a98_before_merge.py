    def _wrap_compute(self, compute):
        @functools.wraps(compute)
        def wrapped_func(*args, **kwargs):
            # return cached value
            if self._computed is not None:
                return self._computed

            if (
                self._to_sync
                and torch.distributed.is_available()  # noqa: W503
                and torch.distributed.is_initialized()  # noqa: W503
            ):
                self._sync_dist()

            self._computed = compute(*args, **kwargs)
            self.reset()

            return self._computed

        return wrapped_func