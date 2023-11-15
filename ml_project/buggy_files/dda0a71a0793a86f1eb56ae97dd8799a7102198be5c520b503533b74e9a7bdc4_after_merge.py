    def __init__(self,
                 redis_address,
                 autoscaling_config,
                 redis_password=None,
                 prefix_cluster_info=False):
        # Initialize the Redis clients.
        ray.state.state._initialize_global_state(
            redis_address, redis_password=redis_password)
        self.redis = ray._private.services.create_redis_client(
            redis_address, password=redis_password)

        # Initialize the gcs stub for getting all node resource usage.
        gcs_address = self.redis.get("GcsServerAddress").decode("utf-8")
        options = (("grpc.enable_http_proxy", 0), )
        gcs_channel = grpc.insecure_channel(gcs_address, options=options)
        self.gcs_node_resources_stub = \
            gcs_service_pb2_grpc.NodeResourceInfoGcsServiceStub(gcs_channel)

        # Set the redis client and mode so _internal_kv works for autoscaler.
        worker = ray.worker.global_worker
        worker.redis_client = self.redis
        worker.mode = 0
        head_node_ip = redis_address.split(":")[0]
        self.load_metrics = LoadMetrics(local_ip=head_node_ip)
        self.last_avail_resources = None
        self.event_summarizer = EventSummarizer()
        self.prefix_cluster_info = prefix_cluster_info
        self.autoscaling_config = autoscaling_config
        self.autoscaler = None

        logger.info("Monitor: Started")