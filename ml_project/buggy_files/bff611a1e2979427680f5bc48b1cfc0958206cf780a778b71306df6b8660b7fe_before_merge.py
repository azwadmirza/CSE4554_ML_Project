    def status(self):
        Status = collections.namedtuple('Status', ['name', 'state', 'provider',
                                                   'ports'])
        status_list = []
        for container in self.instances:
            name = container.get('name')
            if container.get('created'):
                cd = self._docker.containers(filters={'name': name})[0]
                status_list.append(
                    Status(
                        name=name,
                        state=cd.get('Status'),
                        provider=self.provider,
                        ports=cd.get('Ports')))
            else:
                status_list.append(
                    Status(
                        name=name,
                        state="not_created",
                        provider=self.provider,
                        ports=[]))

        return status_list