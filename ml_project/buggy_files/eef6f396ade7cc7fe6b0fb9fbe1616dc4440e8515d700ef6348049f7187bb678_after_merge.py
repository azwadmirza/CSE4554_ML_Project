    async def jsonrpc_file_reflect(self, **kwargs):
        """
        Reflect all the blobs in a file matching the filter criteria

        Usage:
            file_reflect [--sd_hash=<sd_hash>] [--file_name=<file_name>]
                         [--stream_hash=<stream_hash>] [--rowid=<rowid>]
                         [--reflector=<reflector>]

        Options:
            --sd_hash=<sd_hash>          : (str) get file with matching sd hash
            --file_name=<file_name>      : (str) get file with matching file name in the
                                           downloads folder
            --stream_hash=<stream_hash>  : (str) get file with matching stream hash
            --rowid=<rowid>              : (int) get file with matching row id
            --reflector=<reflector>      : (str) reflector server, ip address or url
                                           by default choose a server from the config

        Returns:
            (list) list of blobs reflected
        """

        server, port = kwargs.get('server'), kwargs.get('port')
        if server and port:
            port = int(port)
        else:
            server, port = random.choice(self.conf.reflector_servers)
        reflected = await asyncio.gather(*[
            self.stream_manager.reflect_stream(stream, server, port)
            for stream in self.stream_manager.get_filtered_streams(**kwargs)
        ])
        total = []
        for reflected_for_stream in reflected:
            total.extend(reflected_for_stream)
        return total