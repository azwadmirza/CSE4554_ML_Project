    def yield_execution_pool(self):
        actor_cls = self.get('_actor_cls')
        actor_uid = self.get('_actor_uid')
        op_key = self.get('_op_key')
        if not actor_cls or not actor_uid:  # pragma: no cover
            return

        from .actors import new_client
        from .worker.daemon import WorkerDaemonActor
        client = new_client()

        worker_addr = self.get_local_address()
        if client.has_actor(client.actor_ref(WorkerDaemonActor.default_uid(), address=worker_addr)):
            holder = client.actor_ref(WorkerDaemonActor.default_uid(), address=worker_addr)
        else:
            holder = client
        uid = f'w:0:mars-cpu-calc-backup-{os.getpid()}-{op_key}-{random.randint(-1, 9999)}'
        uid = self._actor_ctx.distributor.make_same_process(uid, actor_uid)
        ref = holder.create_actor(actor_cls, uid=uid, address=worker_addr)
        return ref