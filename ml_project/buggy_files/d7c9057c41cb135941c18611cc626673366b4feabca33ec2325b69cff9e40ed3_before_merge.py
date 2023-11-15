    def compute_action(self, observation):
        return self.policy.compute(observation, update=False)[0]