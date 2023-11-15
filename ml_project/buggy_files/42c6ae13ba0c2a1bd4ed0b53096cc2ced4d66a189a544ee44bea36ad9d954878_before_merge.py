    def set_schedulers(self, schedulers):
        logger.debug('Setting schedulers %r', schedulers)
        self._schedulers = schedulers
        self._hash_ring = create_hash_ring(self._schedulers)

        for observer_ref, fun_name in self._observer_refs:
            # notify the observers to update the new scheduler list
            getattr(observer_ref, fun_name)(schedulers, _tell=True)