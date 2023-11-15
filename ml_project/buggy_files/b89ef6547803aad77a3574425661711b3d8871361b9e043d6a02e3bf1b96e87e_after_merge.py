    async def run(self):
        # Create an aioredis client for all modules.
        try:
            self.aioredis_client = await dashboard_utils.get_aioredis_client(
                self.redis_address, self.redis_password,
                dashboard_consts.CONNECT_REDIS_INTERNAL_SECONDS,
                dashboard_consts.RETRY_REDIS_CONNECTION_TIMES)
        except (socket.gaierror, ConnectionError):
            logger.error(
                "Dashboard head exiting: "
                "Failed to connect to redis at %s", self.redis_address)
            sys.exit(-1)

        # Create a http session for all modules.
        self.http_session = aiohttp.ClientSession(
            loop=asyncio.get_event_loop())

        # Waiting for GCS is ready.
        while True:
            try:
                gcs_address = await self.aioredis_client.get(
                    dashboard_consts.REDIS_KEY_GCS_SERVER_ADDRESS)
                if not gcs_address:
                    raise Exception("GCS address not found.")
                logger.info("Connect to GCS at %s", gcs_address)
                options = (("grpc.enable_http_proxy", 0), )
                channel = aiogrpc.insecure_channel(
                    gcs_address, options=options)
            except Exception as ex:
                logger.error("Connect to GCS failed: %s, retry...", ex)
                await asyncio.sleep(
                    dashboard_consts.CONNECT_GCS_INTERVAL_SECONDS)
            else:
                self.aiogrpc_gcs_channel = channel
                break

        # Create a NodeInfoGcsServiceStub.
        self._gcs_node_info_stub = gcs_service_pb2_grpc.NodeInfoGcsServiceStub(
            self.aiogrpc_gcs_channel)

        # Start a grpc asyncio server.
        await self.server.start()

        async def _async_notify():
            """Notify signals from queue."""
            while True:
                co = await dashboard_utils.NotifyQueue.get()
                try:
                    await co
                except Exception:
                    logger.exception(f"Error notifying coroutine {co}")

        modules = self._load_modules()

        # Http server should be initialized after all modules loaded.
        app = aiohttp.web.Application()
        app.add_routes(routes=routes.bound_routes())

        runner = aiohttp.web.AppRunner(app)
        await runner.setup()
        last_ex = None
        for i in range(1 + self.http_port_retries):
            try:
                site = aiohttp.web.TCPSite(runner, self.http_host,
                                           self.http_port)
                await site.start()
                break
            except OSError as e:
                last_ex = e
                self.http_port += 1
                logger.warning("Try to use port %s: %s", self.http_port, e)
        else:
            raise Exception(f"Failed to find a valid port for dashboard after "
                            f"{self.http_port_retries} retries: {last_ex}")
        http_host, http_port, *_ = site._server.sockets[0].getsockname()
        logger.info("Dashboard head http address: %s:%s", http_host, http_port)

        # Write the dashboard head port to redis.
        await self.aioredis_client.set(ray_constants.REDIS_KEY_DASHBOARD,
                                       f"{http_host}:{http_port}")
        await self.aioredis_client.set(
            dashboard_consts.REDIS_KEY_DASHBOARD_RPC,
            f"{self.ip}:{self.grpc_port}")

        # Dump registered http routes.
        dump_routes = [
            r for r in app.router.routes() if r.method != hdrs.METH_HEAD
        ]
        for r in dump_routes:
            logger.info(r)
        logger.info("Registered %s routes.", len(dump_routes))

        # Freeze signal after all modules loaded.
        dashboard_utils.SignalManager.freeze()
        concurrent_tasks = [
            self._update_nodes(),
            _async_notify(),
            DataOrganizer.purge(),
            DataOrganizer.organize(),
        ]
        await asyncio.gather(*concurrent_tasks,
                             *(m.run(self.server) for m in modules))
        await self.server.wait_for_termination()