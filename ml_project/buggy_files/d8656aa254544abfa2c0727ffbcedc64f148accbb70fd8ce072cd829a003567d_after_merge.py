    def delete(self):
        """Deletes the rule in AWS"""
        self.remove_all_targets()

        try:
            response = self.client.delete_rule(Name=self.name)
        except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
            self.module.fail_json_aws(e, msg="Could not delete rule %s" % self.name)
        self.changed = True
        return response