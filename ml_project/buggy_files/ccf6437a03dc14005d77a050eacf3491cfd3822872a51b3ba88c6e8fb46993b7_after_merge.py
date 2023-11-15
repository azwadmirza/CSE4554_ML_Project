    def barrier(self, *args, **kwargs):
        if torch_distrib.is_initialized():
            hvd.join()