    def post_create(self):
        from .daemon import WorkerDaemonActor
        from .dispatcher import DispatchActor
        from .quota import MemQuotaActor
        from .status import StatusActor

        super().post_create()
        self.set_cluster_info_ref()

        self._dispatch_ref = self.promise_ref(DispatchActor.default_uid())
        self._mem_quota_ref = self.promise_ref(MemQuotaActor.default_uid())

        self._daemon_ref = self.ctx.actor_ref(WorkerDaemonActor.default_uid())
        if not self.ctx.has_actor(self._daemon_ref):
            self._daemon_ref = None
        else:
            self.register_actors_down_handler()

        self._status_ref = self.ctx.actor_ref(StatusActor.default_uid())
        if not self.ctx.has_actor(self._status_ref):
            self._status_ref = None

        self._receiver_manager_ref = self.ctx.actor_ref(ReceiverManagerActor.default_uid())
        if not self.ctx.has_actor(self._receiver_manager_ref):
            self._receiver_manager_ref = None
        else:
            self._receiver_manager_ref = self.promise_ref(self._receiver_manager_ref)

        from ..scheduler import ResourceActor
        self._resource_ref = self.get_actor_ref(ResourceActor.default_uid())

        self.periodical_dump()