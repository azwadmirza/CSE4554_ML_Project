    def status(self):
        Status = collections.namedtuple('Status', ['name', 'state', 'provider',
                                                   'ports'])
        status_list = []
        for container in self.instances:
            name = container.get('name')
            try:
                d = self._docker.containers(filters={'name': name})[0]
                state = d.get('Status')
                ports = d.get('Ports')
            except IndexError:
                state = 'not_created'
                ports = []
            status_list.append(
                Status(
                    name=name,
                    state=state,
                    provider=self.provider,
                    ports=ports))

        return status_list