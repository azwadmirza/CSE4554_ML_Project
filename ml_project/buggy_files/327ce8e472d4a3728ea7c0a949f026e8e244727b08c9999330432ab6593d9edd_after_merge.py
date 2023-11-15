    def register_observer(self, observer, fun_name):
        self._observer_refs[(observer.uid, observer.address)] = (self.ctx.actor_ref(observer), fun_name)