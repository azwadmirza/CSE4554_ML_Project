    def __init__(self, policy, data):
        self.policy = policy
        self.data = data
        self.filters = self.data.get('conditions', [])
        # used by c7n-org to extend evaluation conditions
        self.env_vars = {}