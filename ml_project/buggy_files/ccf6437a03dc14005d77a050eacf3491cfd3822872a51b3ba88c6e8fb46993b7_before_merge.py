    def barrier(self, *args, **kwargs):
        hvd.join()