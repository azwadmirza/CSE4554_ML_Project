    def update_cost(self, config, cost):
        config_id = self.config_ids[config]
        self.cost_per_config[config_id] = cost