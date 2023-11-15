    def set_share_mode(self, share_mode):
        self.get_handle().addCallback(lambda handle: handle.set_share_mode(share_mode))