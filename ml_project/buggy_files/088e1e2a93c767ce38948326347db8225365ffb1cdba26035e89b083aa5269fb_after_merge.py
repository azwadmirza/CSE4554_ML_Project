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

            # Docker version
            # Exemple: {
            #     "KernelVersion": "3.16.4-tinycore64",
            #     "Arch": "amd64",
            #     "ApiVersion": "1.15",
            #     "Version": "1.3.0",
            #     "GitCommit": "c78088f",
            #     "Os": "linux",
            #     "GoVersion": "go1.3.3"
            # }
            try:
                self.stats['version'] = self.docker_client.version()
            except Exception as e:
                # Correct issue#649
                logger.error("{} plugin - Can not get Docker version ({})".format(self.plugin_name, e))
                return self.stats

            # Container globals information
            # Example: [{u'Status': u'Up 36 seconds',
            #            u'Created': 1420378904,
            #            u'Image': u'nginx:1',
            #            u'Ports': [{u'Type': u'tcp', u'PrivatePort': 443},
            #                       {u'IP': u'0.0.0.0', u'Type': u'tcp', u'PublicPort': 8080, u'PrivatePort': 80}],
            #            u'Command': u"nginx -g 'daemon off;'",
            #            u'Names': [u'/webstack_nginx_1'],
            #            u'Id': u'b0da859e84eb4019cf1d965b15e9323006e510352c402d2f442ea632d61faaa5'}]

            # Update current containers list
            try:
                self.stats['containers'] = self.docker_client.containers()
            except Exception as e:
                logger.error("{} plugin - Can not get containers list ({})".format(self.plugin_name, e))
                return self.stats

            # Start new thread for new container
            for container in self.stats['containers']:
                if container['Id'] not in self.thread_list:
                    # Thread did not exist in the internal dict
                    # Create it and add it to the internal dict
                    logger.debug("{} plugin - Create thread for container {}".format(self.plugin_name, container['Id'][:12]))
                    t = ThreadDockerGrabber(self.docker_client, container['Id'])
                    self.thread_list[container['Id']] = t
                    t.start()

            # Stop threads for non-existing containers
            nonexisting_containers = list(set(self.thread_list.keys()) - set([c['Id'] for c in self.stats['containers']]))
            for container_id in nonexisting_containers:
                # Stop the thread
                logger.debug("{} plugin - Stop thread for old container {}".format(self.plugin_name, container_id[:12]))
                self.thread_list[container_id].stop()
                # Delete the item from the dict
                del(self.thread_list[container_id])

            # Get stats for all containers
            for container in self.stats['containers']:
                # The key is the container name and not the Id
                container['key'] = self.get_key()

                # Export name (first name in the list, without the /)
                container['name'] = container['Names'][0][1:]

                container['cpu'] = self.get_docker_cpu(container['Id'], self.thread_list[container['Id']].stats)
                container['memory'] = self.get_docker_memory(container['Id'], self.thread_list[container['Id']].stats)
                container['network'] = self.get_docker_network(container['Id'], self.thread_list[container['Id']].stats)

        elif self.input_method == 'snmp':
            # Update stats using SNMP
            # Not available
            pass

        return self.stats