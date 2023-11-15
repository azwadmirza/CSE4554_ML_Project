    def put_targets(self, targets):
        """Creates or updates the provided targets on the rule in AWS"""
        if not targets:
            return
        request = {
            'Rule': self.name,
            'Targets': self._targets_request(targets),
        }
        try:
            response = self.client.put_targets(**request)
        except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
            self.module.fail_json_aws(e, msg="Could not create/update rule targets for rule %s" % self.name)
        self.changed = True
        return response