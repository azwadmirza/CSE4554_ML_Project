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
        response = self.client.put_rule(**request)
        self.changed = True
        return response