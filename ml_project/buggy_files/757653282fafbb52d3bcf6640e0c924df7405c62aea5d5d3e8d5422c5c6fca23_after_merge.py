    def _fast_memory_load(self, addr):
        """
        Perform a fast memory loading of static content from static regions, a.k.a regions that are mapped to the
        memory by the loader.

        :param int addr: Address to read from.
        :return: A tuple of the data (cffi.CData) and the max size in the current continuous block, or (None, None) if
                 the address does not exist.
        :rtype: tuple
        """

        try:
            buff, size = self.project.loader.memory.read_bytes_c(addr)
            return buff, size

        except KeyError:
            return None, None