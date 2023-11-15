    def memory_maps(self):
        with catch_zombie(self):
            return cext.proc_memory_maps(self.pid)