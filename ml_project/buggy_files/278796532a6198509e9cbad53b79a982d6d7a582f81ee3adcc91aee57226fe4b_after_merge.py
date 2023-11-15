    def __init__(self, client, results):

        super(SwarmManager, self).__init__()

        self.client = client
        self.results = results
        self.check_mode = self.client.check_mode
        self.swarm_info = {}

        self.state = client.module.params['state']
        self.force = client.module.params['force']

        self.differences = DifferenceTracker()
        self.parameters = TaskParameters.from_ansible_params(client)