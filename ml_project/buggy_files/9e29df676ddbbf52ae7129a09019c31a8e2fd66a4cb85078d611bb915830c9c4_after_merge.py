    async def _get_services(self, host: IPv4Address, timeout: int):
        port = int(os.environ.get("PYATV_UDNS_PORT", 5353))  # For testing purposes
        services = [s[0:-1] for s in ALL_SERVICES]
        try:
            await knock.knock(host, KNOCK_PORTS, self.loop)
            response = await udns.request(
                self.loop, str(host), services, port=port, timeout=timeout
            )
        except asyncio.TimeoutError:
            response = None
        return host, response