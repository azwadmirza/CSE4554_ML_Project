    def broadcast(self, obj, src=0):
        self.barrier()
        obj = hvd.broadcast_object(obj, src)
        return obj