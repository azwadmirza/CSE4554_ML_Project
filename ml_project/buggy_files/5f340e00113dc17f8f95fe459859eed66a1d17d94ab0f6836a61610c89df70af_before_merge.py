    def get_cost(self, config):
        config_id = self.config_ids[config.__repr__()]
        return self.cost_per_config[config_id]