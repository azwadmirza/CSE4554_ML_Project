    def start(self, endpoint, schedulers, pool):
        """
        there are two way to start a scheduler
        1) if options.kv_store is specified as an etcd address, the endpoint will be written
        into kv-storage to indicate that this scheduler is one the schedulers,
        and the etcd is used as a service discover.
        2) if options.kv_store is not an etcd address, there will be only one scheduler
        """
        kv_store = kvstore.get(options.kv_store)
        kv_store.write('/schedulers/%s' % endpoint, dir=True)

        if not isinstance(kv_store, kvstore.LocalKVStore):
            # set etcd as service discover
            logger.info('Mars Scheduler started with kv store %s.', options.kv_store)
            service_discover_addr = options.kv_store
            all_schedulers = None
            # create KVStoreActor when there is a distributed KV store
            self._kv_store_ref = pool.create_actor(KVStoreActor, uid=KVStoreActor.default_name())
        else:
            # single scheduler
            logger.info('Mars Scheduler started in standalone mode.')
            service_discover_addr = None
            all_schedulers = {endpoint}
            if isinstance(schedulers, six.string_types):
                schedulers = schedulers.split(',')
            if schedulers:
                all_schedulers.update(schedulers)
            all_schedulers = list(all_schedulers)

        # create ClusterInfoActor
        self._cluster_info_ref = pool.create_actor(
            ClusterInfoActor, all_schedulers, service_discover_addr, uid=ClusterInfoActor.default_name())
        # create ChunkMetaActor
        self._chunk_meta_ref = pool.create_actor(ChunkMetaActor, uid=ChunkMetaActor.default_name())
        # create SessionManagerActor
        self._session_manager_ref = pool.create_actor(
            SessionManagerActor, uid=SessionManagerActor.default_name())
        # create AssignerActor
        self._assigner_ref = pool.create_actor(AssignerActor, uid=AssignerActor.default_name())
        # create ResourceActor
        self._resource_ref = pool.create_actor(ResourceActor, uid=ResourceActor.default_name())
        # create NodeInfoActor
        self._node_info_ref = pool.create_actor(NodeInfoActor, uid=NodeInfoActor.default_name())
        kv_store.write('/schedulers/%s/meta' % endpoint,
                       json.dumps(self._resource_ref.get_workers_meta()))
        # create ResultReceiverActor
        self._result_receiver_ref = pool.create_actor(ResultReceiverActor, uid=ResultReceiverActor.default_name())