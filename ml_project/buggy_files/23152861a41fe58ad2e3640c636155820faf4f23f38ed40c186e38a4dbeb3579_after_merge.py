    def describe(self):
        """Returns the existing details of the rule in AWS"""
        try:
            rule_info = self.client.describe_rule(Name=self.name)
        except botocore.exceptions.ClientError as e:
            error_code = e.response.get('Error', {}).get('Code')
            if error_code == 'ResourceNotFoundException':
                return {}
            self.module.fail_json_aws(e, msg="Could not describe rule %s" % self.name)
        except botocore.exceptions.BotoCoreError as e:
            self.module.fail_json_aws(e, msg="Could not describe rule %s" % self.name)
        return self._snakify(rule_info)