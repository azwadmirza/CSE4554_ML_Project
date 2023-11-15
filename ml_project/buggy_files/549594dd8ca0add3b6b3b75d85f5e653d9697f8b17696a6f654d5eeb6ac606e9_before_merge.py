    def unregister(self, obj):
        if hasattr(obj, 'rule'):  # commands and intents have it added
            for rule in obj.rule:
                self._callables[obj.priority][rule].remove(obj)
        if hasattr(obj, 'interval'):
            # TODO this should somehow find the right job to remove, rather than
            # clearing the entire queue. Issue #831
            self.scheduler.clear_jobs()
        if getattr(obj, '__name__', None) == 'shutdown':
            self.shutdown_methods.remove(obj)