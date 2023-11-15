    def get_arena(self, arena_addr=None):
        """Read a malloc_state struct from the specified address, default to
        reading the current thread's arena. Return the main arena if the
        current thread is not attached to an arena.
        """
        if arena_addr is None:
            if self.multithreaded:
                arena_addr = pwndbg.memory.u(pwndbg.symbol.address('thread_arena'))
                if arena_addr != 0:
                    return pwndbg.memory.poi(self.malloc_state, arena_addr)

            return self.main_arena

        try:
            return pwndbg.memory.poi(self.malloc_state, arena_addr)
        except gdb.MemoryError:
            # print(message.warn('Bad arena address {}'.format(arena_addr.address)))
            return None