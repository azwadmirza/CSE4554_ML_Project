    def init_pool_manager(
        self,
        proxy: typing.Optional[Proxy],
        ssl_context: ssl.SSLContext,
        num_pools: int,
        maxsize: int,
        block: bool,
    ) -> typing.Union[urllib3.PoolManager, urllib3.ProxyManager]:
        if proxy is None:
            return urllib3.PoolManager(
                ssl_context=ssl_context,
                num_pools=num_pools,
                maxsize=maxsize,
                block=block,
            )
        else:
            return urllib3.ProxyManager(
                proxy_url=str(proxy.url),
                proxy_headers=dict(proxy.headers),
                ssl_context=ssl_context,
                num_pools=num_pools,
                maxsize=maxsize,
                block=block,
            )