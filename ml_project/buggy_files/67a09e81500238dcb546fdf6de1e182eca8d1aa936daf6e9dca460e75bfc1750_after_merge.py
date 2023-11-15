    def memory_maps(self):
        return cext.proc_memory_maps(self.pid)