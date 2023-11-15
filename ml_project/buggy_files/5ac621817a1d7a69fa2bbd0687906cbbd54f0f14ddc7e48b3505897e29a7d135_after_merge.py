    def get_diff(self, rollback_id=None):
        diff = {'config_diff': None}
        response = self.compare_configuration(rollback_id=rollback_id)
        if response:
            diff['config_diff'] = response
        return diff