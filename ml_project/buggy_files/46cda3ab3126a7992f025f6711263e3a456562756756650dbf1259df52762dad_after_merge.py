    def get_actual_capacity(self, store_limit):
        """
        Get actual capacity of plasma store
        :return: actual storage size in bytes
        """
        try:
            store_limit = min(store_limit, self._plasma_client.store_capacity())
        except AttributeError:  # pragma: no cover
            pass

        if self._size_limit is None:
            left_size = store_limit
            alloc_fraction = 1
            while True:
                allocate_size = int(left_size * alloc_fraction / PAGE_SIZE) * PAGE_SIZE
                try:
                    obj_id = plasma.ObjectID.from_random()
                    buf = [self._plasma_client.create(obj_id, allocate_size)]
                    self._plasma_client.seal(obj_id)
                    del buf[:]
                    break
                except plasma_errors.PlasmaStoreFull:
                    alloc_fraction *= 0.99
                finally:
                    self._plasma_client.evict(allocate_size)
            self._size_limit = allocate_size
        return self._size_limit