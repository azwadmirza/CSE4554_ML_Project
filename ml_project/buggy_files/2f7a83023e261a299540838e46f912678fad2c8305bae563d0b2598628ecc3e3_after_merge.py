    def remove_targets(self, target_ids):
        """Removes the provided targets from the rule in AWS"""
        if not target_ids:
            return
        request = {
            'Rule': self.name,
            'Ids': target_ids
        }
        try:
            response = self.client.remove_targets(**request)
        except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
            self.module.fail_json_aws(e, msg="Could not remove rule targets from rule %s" % self.name)
        self.changed = True
        return response