    def delInstance(cls, *args, **kw):
        with cls.__singleton_lock:
            GUIDBProducer.__single = None