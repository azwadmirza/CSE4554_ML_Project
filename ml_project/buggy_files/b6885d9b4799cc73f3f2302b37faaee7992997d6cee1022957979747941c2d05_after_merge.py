    def enable(self):
        """Enables the rule in AWS"""
        try:
            response = self.client.enable_rule(Name=self.name)
        except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
            self.module.fail_json_aws(e, msg="Could not enable rule %s" % self.name)
        self.changed = True
        return response