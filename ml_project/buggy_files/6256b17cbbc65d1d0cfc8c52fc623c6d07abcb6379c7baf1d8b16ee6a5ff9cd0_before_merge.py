    async def do_run(self, event_bus: EndpointAPI) -> None:
        boot_info = self._boot_info

        if boot_info.args.enable_metrics:
            metrics_service = metrics_service_from_args(boot_info.args, AsyncioMetricsService)
        else:
            # Use a NoopMetricsService so that no code branches need to be taken if metrics
            # are disabled
            metrics_service = NOOP_METRICS_SERVICE

        trinity_config = boot_info.trinity_config
        NodeClass = trinity_config.get_app_config(Eth1AppConfig).node_class
        node = NodeClass(event_bus, metrics_service, trinity_config)
        strategy = self.get_active_strategy(boot_info)

        async with background_asyncio_service(node) as node_manager:
            sync_task = create_task(
                self.launch_sync(node, strategy, boot_info, event_bus), self.name)
            # The Node service is our responsibility, so we must exit if either that or the syncer
            # returns.
            node_manager_task = create_task(
                node_manager.wait_finished(), f'{NodeClass.__name__} wait_finished() task')
            await wait_first([sync_task, node_manager_task], max_wait_after_cancellation=2)