    def post_create(self):
        super().post_create()
        try:
            self.set_cluster_info_ref()
        except ActorNotExist:
            pass

        from .status import StatusActor
        self._status_ref = self.ctx.actor_ref(StatusActor.default_uid())
        if not self.ctx.has_actor(self._status_ref):
            self._status_ref = None