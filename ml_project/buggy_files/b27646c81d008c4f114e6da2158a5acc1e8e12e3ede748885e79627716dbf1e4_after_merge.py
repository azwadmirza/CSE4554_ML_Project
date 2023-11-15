    def put(self, enabled=True):
        """Creates or updates the rule in AWS"""
        request = {
            'Name': self.name,
            'State': "ENABLED" if enabled else "DISABLED",
        }
        if self.schedule_expression:
            request['ScheduleExpression'] = self.schedule_expression
        if self.event_pattern:
            request['EventPattern'] = self.event_pattern
        if self.description:
            request['Description'] = self.description
        if self.role_arn:
            request['RoleArn'] = self.role_arn
        try:
            response = self.client.put_rule(**request)
        except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
            self.module.fail_json_aws(e, msg="Could not create/update rule %s" % self.name)
        self.changed = True
        return response