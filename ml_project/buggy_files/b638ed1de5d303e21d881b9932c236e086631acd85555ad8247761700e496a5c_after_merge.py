    def disable(self):
        """Disables the rule in AWS"""
        try:
            response = self.client.disable_rule(Name=self.name)
        except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
            self.module.fail_json_aws(e, msg="Could not disable rule %s" % self.name)
        self.changed = True
        return response