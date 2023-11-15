    def _next_code_addr(self):

        while True:
            addr = self._next_code_addr_core()
            if addr is None:
                return None

            # if the new address is already occupied
            if not self._seg_list.is_occupied(addr):
                return addr