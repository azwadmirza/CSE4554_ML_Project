    def unregister(self, obj):
        if not callable(obj):
            return
        if hasattr(obj, 'rule'):  # commands and intents have it added
            for rule in obj.rule:
                callb_list = self._callables[obj.priority][rule]
                if obj in callb_list:
                    callb_list.remove(obj)
        if hasattr(obj, 'interval'):
            # TODO this should somehow find the right job to remove, rather than
            # clearing the entire queue. Issue #831
            self.scheduler.clear_jobs()
        if (getattr(obj, '__name__', None) == 'shutdown'
                and obj in self.shutdown_methods):
            self.shutdown_methods.remove(obj)