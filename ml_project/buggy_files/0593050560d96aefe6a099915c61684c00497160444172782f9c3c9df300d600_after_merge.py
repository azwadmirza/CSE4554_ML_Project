    def post_create(self):
        from ..dispatcher import DispatchActor
        from ..status import StatusActor

        super().post_create()
        self.register_actors_down_handler()
        self._dispatch_ref = self.promise_ref(DispatchActor.default_uid())

        parse_num, is_percent = parse_readable_size(options.worker.min_spill_size)
        self._min_spill_size = int(self._size_limit * parse_num if is_percent else parse_num)
        parse_num, is_percent = parse_readable_size(options.worker.max_spill_size)
        self._max_spill_size = int(self._size_limit * parse_num if is_percent else parse_num)

        status_ref = self.ctx.actor_ref(StatusActor.default_uid())
        self._status_ref = status_ref if self.ctx.has_actor(status_ref) else None

        self._storage_handler = self.storage_client.get_storage_handler(
            self._storage_device.build_location(self.proc_id))

        self.ref().update_cache_status(_tell=True)