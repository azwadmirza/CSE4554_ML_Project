    def default_host_ip(self):
        ip = '0.0.0.0'
        if not self.networks:
            return ip
        for net in self.networks:
            if net.get('name'):
                try:
                    network = self.client.inspect_network(net['name'])
                    if network.get('Driver') == 'bridge' and \
                       network.get('Options', {}).get('com.docker.network.bridge.host_binding_ipv4'):
                        ip = network['Options']['com.docker.network.bridge.host_binding_ipv4']
                        break
                except NotFound as e:
                    self.client.fail(
                        "Cannot inspect the network '{0}' to determine the default IP.".format(net['name']),
                        exception=traceback.format_exc()
                    )
        return ip