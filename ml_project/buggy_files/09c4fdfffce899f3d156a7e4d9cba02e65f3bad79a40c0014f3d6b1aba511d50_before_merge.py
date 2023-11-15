    def _ensure_rules_action_has_arn(self, rules):
        """
        If a rule Action has been passed with a Target Group Name instead of ARN, lookup the ARN and
        replace the name.

        :param rules: a list of rule dicts
        :return: the same list of dicts ensuring that each rule Actions dict has TargetGroupArn key. If a TargetGroupName key exists, it is removed.
        """

        for rule in rules:
            if 'TargetGroupName' in rule['Actions'][0]:
                rule['Actions'][0]['TargetGroupArn'] = convert_tg_name_to_arn(self.connection, self.module, rule['Actions'][0]['TargetGroupName'])
                del rule['Actions'][0]['TargetGroupName']

        return rules