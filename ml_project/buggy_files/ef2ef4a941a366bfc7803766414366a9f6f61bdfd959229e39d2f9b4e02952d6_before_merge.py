    def __init__(self, policy, data):
        self.policy = policy
        self.data = data
        self.filters = self.data.get('conditions', [])
        # for value_from usage / we use the conditions class
        # to mimic a resource manager interface. we can't use
        # the actual resource manager as we're overriding block
        # filters which work w/ resource type metadata and our
        # resource here is effectively the execution variables.
        self.config = self.policy.options
        rm = self.policy.resource_manager
        self._cache = rm._cache
        self.session_factory = rm.session_factory
        # used by c7n-org to extend evaluation conditions
        self.env_vars = {}