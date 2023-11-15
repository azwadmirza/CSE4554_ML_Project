    def register_observer(self, observer, fun_name):
        self._observer_refs.append((self.ctx.actor_ref(observer), fun_name))