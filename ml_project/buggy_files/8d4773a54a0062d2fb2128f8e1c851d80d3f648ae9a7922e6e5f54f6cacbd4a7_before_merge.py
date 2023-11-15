    def _compare_rule(self, current_rule, new_rule):
        """

        :return:
        """

        modified_rule = {}

        # Priority
        if current_rule['Priority'] != new_rule['Priority']:
            modified_rule['Priority'] = new_rule['Priority']

        # Actions
        #   We wont worry about the Action Type because it is always 'forward'
        if current_rule['Actions'][0]['TargetGroupArn'] != new_rule['Actions'][0]['TargetGroupArn']:
            modified_rule['Actions'] = []
            modified_rule['Actions'].append({})
            modified_rule['Actions'][0]['TargetGroupArn'] = new_rule['Actions'][0]['TargetGroupArn']
            modified_rule['Actions'][0]['Type'] = 'forward'

        # Conditions
        modified_conditions = []
        for condition in new_rule['Conditions']:
            if not self._compare_condition(current_rule['Conditions'], condition):
                modified_conditions.append(condition)

        if modified_conditions:
            modified_rule['Conditions'] = modified_conditions

        return modified_rule