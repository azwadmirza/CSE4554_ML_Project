    def _get_raw_servers(self):
        # pylint: disable=cell-var-from-loop
        """Get a map of unparsed all server blocks
        """
        servers = {}
        for filename in self.parsed:
            tree = self.parsed[filename]
            servers[filename] = []
            srv = servers[filename]  # workaround undefined loop var in lambdas

            # Find all the server blocks
            _do_for_subarray(tree, lambda x: x[0] == ['server'],
                             lambda x, y: srv.append((x[1], y)))

            # Find 'include' statements in server blocks and append their trees
            for i, (server, path) in enumerate(servers[filename]):
                new_server = self._get_included_directives(server)
                servers[filename][i] = (new_server, path)
        return servers