    async def on_socks5_tcp_data(self, tcp_connection, destination, request):
        self._logger.debug('Got request for %s: %s', destination, request)
        hops = self.socks_servers.index(tcp_connection.socksserver) + 1
        try:
            response = await self.tunnel_community.perform_http_request(destination, request, hops)
            self._logger.debug('Got response from %s: %s', destination, response)
        except RuntimeError as e:
            self._logger.info('Failed to get HTTP response using tunnels: %s', e)
            return
        tcp_connection.transport.write(response)