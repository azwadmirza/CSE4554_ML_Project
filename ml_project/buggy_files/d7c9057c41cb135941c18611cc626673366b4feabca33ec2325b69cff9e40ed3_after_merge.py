    def compute_action(self, observation, *args, **kwargs):
        return self.policy.compute(observation, update=False)[0]