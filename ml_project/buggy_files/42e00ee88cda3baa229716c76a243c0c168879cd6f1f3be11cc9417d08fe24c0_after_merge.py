    async def run(self):
        async def _check_parent():
            """Check if raylet is dead and fate-share if it is."""
            try:
                curr_proc = psutil.Process()
                while True:
                    parent = curr_proc.parent()
                    if (parent is None or parent.pid == 1
                            or self.ppid != parent.pid):
                        logger.error("Raylet is dead, exiting.")
                        sys.exit(0)
                    await asyncio.sleep(
                        dashboard_consts.
                        DASHBOARD_AGENT_CHECK_PARENT_INTERVAL_SECONDS)
            except Exception:
                logger.error("Failed to check parent PID, exiting.")
                sys.exit(1)

        if sys.platform not in ["win32", "cygwin"]:
            check_parent_task = create_task(_check_parent())

        # Create an aioredis client for all modules.
        try:
            self.aioredis_client = await dashboard_utils.get_aioredis_client(
                self.redis_address, self.redis_password,
                dashboard_consts.CONNECT_REDIS_INTERNAL_SECONDS,
                dashboard_consts.RETRY_REDIS_CONNECTION_TIMES)
        except (socket.gaierror, ConnectionRefusedError):
            logger.error(
                "Dashboard agent exiting: "
                "Failed to connect to redis at %s", self.redis_address)
            sys.exit(-1)

        # Create a http session for all modules.
        self.http_session = aiohttp.ClientSession(
            loop=asyncio.get_event_loop())

        # Start a grpc asyncio server.
        await self.server.start()

        modules = self._load_modules()

        # Http server should be initialized after all modules loaded.
        app = aiohttp.web.Application()
        app.add_routes(routes=routes.bound_routes())

        # Enable CORS on all routes.
        cors = aiohttp_cors.setup(
            app,
            defaults={
                "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers="*",
                    allow_methods="*",
                    allow_headers=("Content-Type", "X-Header"),
                )
            })
        for route in list(app.router.routes()):
            cors.add(route)

        runner = aiohttp.web.AppRunner(app)
        await runner.setup()
        site = aiohttp.web.TCPSite(runner, self.ip, 0)
        await site.start()
        http_host, http_port, *_ = site._server.sockets[0].getsockname()
        logger.info("Dashboard agent http address: %s:%s", http_host,
                    http_port)

        # Dump registered http routes.
        dump_routes = [
            r for r in app.router.routes() if r.method != hdrs.METH_HEAD
        ]
        for r in dump_routes:
            logger.info(r)
        logger.info("Registered %s routes.", len(dump_routes))

        # Write the dashboard agent port to redis.
        await self.aioredis_client.set(
            f"{dashboard_consts.DASHBOARD_AGENT_PORT_PREFIX}{self.node_id}",
            json.dumps([http_port, self.grpc_port]))

        # Register agent to agent manager.
        raylet_stub = agent_manager_pb2_grpc.AgentManagerServiceStub(
            self.aiogrpc_raylet_channel)

        await raylet_stub.RegisterAgent(
            agent_manager_pb2.RegisterAgentRequest(
                agent_pid=os.getpid(),
                agent_port=self.grpc_port,
                agent_ip_address=self.ip))

        tasks = [m.run(self.server) for m in modules]
        if sys.platform not in ["win32", "cygwin"]:
            tasks.append(check_parent_task)
        await asyncio.gather(*tasks)

        await self.server.wait_for_termination()
        # Wait for finish signal.
        await runner.cleanup()