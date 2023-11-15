    def add(self, func):
        rule = self.get(func.name)
        params = self.get_rule_params(func)

        if rule and self.delta(rule, params):
            log.debug("Updating config rule for %s" % self)
            rule.update(params)
            return self.client.put_config_rule(ConfigRule=rule)
        elif rule:
            log.debug("Config rule up to date")
            return
        client = self.session.client('lambda')
        try:
            client.add_permission(
                FunctionName=func.name,
                StatementId=func.name,
                SourceAccount=func.arn.split(':')[4],
                Action='lambda:InvokeFunction',
                Principal='config.amazonaws.com')
        except client.exceptions.ResourceConflictException:
            pass

        log.debug("Adding config rule for %s" % func.name)
        return self.client.put_config_rule(ConfigRule=params)