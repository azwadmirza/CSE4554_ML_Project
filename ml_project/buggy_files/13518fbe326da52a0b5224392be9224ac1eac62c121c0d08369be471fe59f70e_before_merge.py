    def __init__(self, client):
        self.client = client
        self.parameters = TaskParameters(client)
        self.check_mode = self.client.check_mode
        self.results = {
            u'changed': False,
            u'actions': []
        }
        self.diff = self.client.module._diff

        self.existing_network = self.get_existing_network()

        if not self.parameters.connected and self.existing_network:
            self.parameters.connected = container_names_in_network(self.existing_network)

        if self.parameters.ipam_options:
            self.parameters.ipam_config = [self.parameters.ipam_options]

        state = self.parameters.state
        if state == 'present':
            self.present()
        elif state == 'absent':
            self.absent()