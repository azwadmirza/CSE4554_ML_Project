    def set_priority(self, prio):
        self.get_handle().addCallback(lambda handle: handle.set_priority(prio))