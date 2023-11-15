    def tribler_started(self):
        async def signal_handler(sig):
            print(f"Received shut down signal {sig}")  # noqa: T001
            if not self._stopping:
                self._stopping = True
                await self.session.shutdown()
                get_event_loop().stop()

        signal.signal(signal.SIGINT, lambda sig, _: ensure_future(signal_handler(sig)))
        signal.signal(signal.SIGTERM, lambda sig, _: ensure_future(signal_handler(sig)))

        self.register_task("bootstrap",  self.session.tunnel_community.bootstrap, interval=30)

        # Remove all logging handlers
        root_logger = logging.getLogger()
        handlers = root_logger.handlers
        for handler in handlers:
            root_logger.removeHandler(handler)
        logging.getLogger().setLevel(logging.ERROR)

        new_strategies = []
        with self.session.ipv8.overlay_lock:
            for strategy, target_peers in self.session.ipv8.strategies:
                if strategy.overlay == self.session.tunnel_community:
                    new_strategies.append((strategy, -1))
                else:
                    new_strategies.append((strategy, target_peers))
            self.session.ipv8.strategies = new_strategies