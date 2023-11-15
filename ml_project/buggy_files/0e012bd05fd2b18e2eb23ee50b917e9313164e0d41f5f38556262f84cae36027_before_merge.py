    def broadcast(self, obj, src=0):
        obj = hvd.broadcast_object(obj, src)
        return obj