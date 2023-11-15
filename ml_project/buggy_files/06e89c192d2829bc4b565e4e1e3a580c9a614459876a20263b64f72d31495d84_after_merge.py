    def delInstance(cls, *args, **kw):
        if GUIDBProducer.hasInstance():
            GUIDBProducer.__single.cancel_all_pending_tasks()
        with cls.__singleton_lock:
            GUIDBProducer.__single = None