    def get_cost(self, config):
        config_id = self.config_ids[config]
        return self.cost_per_config[config_id]