    def _close(self, fast=False):
        """ Send close signal and wait until scheduler completes """
        self.status = 'closing'

        with log_errors():
            _del_global_client(self)
            for pc in self._periodic_callbacks.values():
                pc.stop()
            self._scheduler_identity = {}
            with ignoring(AttributeError):
                dask.config.set(scheduler=self._previous_scheduler)
            with ignoring(AttributeError):
                dask.config.set(shuffle=self._previous_shuffle)
            if self.get == dask.config.get('get', None):
                del dask.config.config['get']
            if self.status == 'closed':
                raise gen.Return()

            if self.scheduler_comm and self.scheduler_comm.comm and not self.scheduler_comm.comm.closed():
                self._send_to_scheduler({'op': 'close-client'})
                self._send_to_scheduler({'op': 'close-stream'})

            # Give the scheduler 'stream-closed' message 100ms to come through
            # This makes the shutdown slightly smoother and quieter
            with ignoring(AttributeError, gen.TimeoutError):
                yield gen.with_timeout(timedelta(milliseconds=100),
                                       self._handle_scheduler_coroutine,
                                       quiet_exceptions=(CancelledError,))

            if self.scheduler_comm and self.scheduler_comm.comm and not self.scheduler_comm.comm.closed():
                yield self.scheduler_comm.close()
            for key in list(self.futures):
                self._release_key(key=key)
            if self._start_arg is None:
                with ignoring(AttributeError):
                    yield self.cluster._close()
            self.status = 'closed'
            if _get_global_client() is self:
                _set_global_client(None)
            coroutines = set(self.coroutines)
            for f in self.coroutines:
                # cancel() works on asyncio futures (Tornado 5)
                # but is a no-op on Tornado futures
                with ignoring(RuntimeError):
                    f.cancel()
                if f.cancelled():
                    coroutines.remove(f)
            del self.coroutines[:]
            if not fast:
                with ignoring(TimeoutError):
                    yield gen.with_timeout(timedelta(seconds=2),
                                           list(coroutines))
            with ignoring(AttributeError):
                self.scheduler.close_rpc()
            self.scheduler = None

        self.status = 'closed'