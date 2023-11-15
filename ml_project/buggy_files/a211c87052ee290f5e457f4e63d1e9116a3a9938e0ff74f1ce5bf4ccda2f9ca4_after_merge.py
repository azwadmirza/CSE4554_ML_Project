        async def signal_handler(sig):
            print(f"Received shut down signal {sig}")  # noqa: T001
            if not self._stopping:
                self._stopping = True
                await self.session.shutdown()
                get_event_loop().stop()