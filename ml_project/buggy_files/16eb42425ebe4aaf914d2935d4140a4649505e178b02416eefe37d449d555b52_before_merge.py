    def watch_workers(self):
        from kubernetes import client, config

        cls = type(self)
        worker_set = set()
        workers_from_resource = set()

        if os.environ.get('KUBE_API_ADDRESS'):  # pragma: no cover
            k8s_config = client.Configuration()
            k8s_config.host = os.environ['KUBE_API_ADDRESS']
        else:
            k8s_config = config.load_incluster_config()

        watcher = self.watcher_cls(k8s_config, os.environ['MARS_K8S_POD_NAMESPACE'])

        for workers in watcher.watch_workers():  # pragma: no branch
            if not cls._watcher_running:  # pragma: no cover
                break

            if self._resource_ref is None:
                self.set_schedulers(self._cluster_info_ref.get_schedulers())
                self._resource_ref = self.get_actor_ref(ResourceActor.default_uid())
            if self._resource_ref is not None:  # pragma: no branch
                workers_from_resource = set(self._resource_ref.get_worker_endpoints())

            removed = (worker_set - set(workers)) or (worker_set - set(workers_from_resource))
            if removed:
                logger.debug('Remove of workers %r detected by kubernetes.', removed)
                if self._resource_ref:  # pragma: no branch
                    self._resource_ref.detach_dead_workers(list(removed), _tell=True, _wait=False)
            worker_set = set(workers)