    def update(self):
        """Update Docker stats using the input method."""
        # Reset stats
        self.reset()

        # Get the current Docker API client
        if not self.docker_client:
            # First time, try to connect to the server
            self.docker_client = self.connect()
            if self.docker_client is None:
                global docker_tag
                docker_tag = False

        # The Docker-py lib is mandatory
        if not docker_tag or (self.args is not None and self.args.disable_docker):
            return self.stats

        if self.input_method == 'local':
            # Update stats
            # Exemple: {
            #     "KernelVersion": "3.16.4-tinycore64",
            #     "Arch": "amd64",
            #     "ApiVersion": "1.15",
            #     "Version": "1.3.0",
            #     "GitCommit": "c78088f",
            #     "Os": "linux",
            #     "GoVersion": "go1.3.3"
            # }
            self.stats['version'] = self.docker_client.version()
            # Example: [{u'Status': u'Up 36 seconds',
            #            u'Created': 1420378904,
            #            u'Image': u'nginx:1',
            #            u'Ports': [{u'Type': u'tcp', u'PrivatePort': 443},
            #                       {u'IP': u'0.0.0.0', u'Type': u'tcp', u'PublicPort': 8080, u'PrivatePort': 80}],
            #            u'Command': u"nginx -g 'daemon off;'",
            #            u'Names': [u'/webstack_nginx_1'],
            #            u'Id': u'b0da859e84eb4019cf1d965b15e9323006e510352c402d2f442ea632d61faaa5'}]
            self.stats['containers'] = self.docker_client.containers()
            # Get stats for all containers
            for c in self.stats['containers']:
                if not hasattr(self, 'docker_stats'):
                    # Create a dict with all the containers' stats instance
                    self.docker_stats = {}

                # TODO: Find a way to correct this
                # The following optimization is not compatible with the network stats
                # The self.docker_client.stats method should be call every time in order to have network stats refreshed
                # Nevertheless, if we call it every time, Glances is slow...
                if c['Id'] not in self.docker_stats:
                    # Create the stats instance for the current container
                    try:
                        self.docker_stats[c['Id']] = self.docker_client.stats(c['Id'], decode=True)
                        logger.debug("Create Docker stats object for container {}".format(c['Id']))
                    except (AttributeError, docker.errors.InvalidVersion) as e:
                        logger.error("Can not call Docker stats method {}".format(e))

                # Get the docker stats
                try:
                    # self.docker_stats[c['Id']] = self.docker_client.stats(c['Id'], decode=True)
                    all_stats = self.docker_stats[c['Id']].next()
                except Exception:
                    all_stats = {}

                c['cpu'] = self.get_docker_cpu(c['Id'], all_stats)
                c['memory'] = self.get_docker_memory(c['Id'], all_stats)
                # c['network'] = self.get_docker_network(c['Id'], all_stats)

        elif self.input_method == 'snmp':
            # Update stats using SNMP
            # Not available
            pass

        return self.stats