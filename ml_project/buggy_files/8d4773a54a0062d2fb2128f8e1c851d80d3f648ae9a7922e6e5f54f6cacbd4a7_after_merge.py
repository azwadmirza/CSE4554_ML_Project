    def _compare_rule(self, current_rule, new_rule):
        """

        :return:
        """

        modified_rule = {}

        # Priority
        if int(current_rule['Priority']) != new_rule['Priority']:
            modified_rule['Priority'] = new_rule['Priority']

        # Actions

        # Check proper rule format on current listener
        if len(current_rule['Actions']) > 1:
            for action in current_rule['Actions']:
                if 'Order' not in action:
                    self.module.fail_json(msg="'Order' key not found in actions. "
                                              "installed version of botocore does not support "
                                              "multiple actions, please upgrade botocore to version "
                                              "1.10.30 or higher")

        # If the lengths of the actions are the same, we'll have to verify that the
        # contents of those actions are the same
        if len(current_rule['Actions']) == len(new_rule['Actions']):
            # if actions have just one element, compare the contents and then update if
            # they're different
            if len(current_rule['Actions']) == 1 and len(new_rule['Actions']) == 1:
                if current_rule['Actions'] != new_rule['Actions']:
                    modified_rule['Actions'] = new_rule['Actions']
                    print("modified_rule:")
                    print(new_rule['Actions'])
            # if actions have multiple elements, we'll have to order them first before comparing.
            # multiple actions will have an 'Order' key for this purpose
            else:
                current_actions_sorted = sorted(current_rule['Actions'], key=lambda x: x['Order'])
                new_actions_sorted = sorted(new_rule['Actions'], key=lambda x: x['Order'])

                # the AWS api won't return the client secret, so we'll have to remove it
                # or the module will always see the new and current actions as different
                # and try to apply the same config
                new_actions_sorted_no_secret = []
                for action in new_actions_sorted:
                    # the secret is currently only defined in the oidc config
                    if action['Type'] == 'authenticate-oidc':
                        action['AuthenticateOidcConfig'].pop('ClientSecret')
                        new_actions_sorted_no_secret.append(action)
                    else:
                        new_actions_sorted_no_secret.append(action)

                if current_actions_sorted != new_actions_sorted_no_secret:
                    modified_rule['Actions'] = new_rule['Actions']
                    print("modified_rule:")
                    print(new_rule['Actions'])
        # If the action lengths are different, then replace with the new actions
        else:
            modified_rule['Actions'] = new_rule['Actions']
            print("modified_rule:")
            print(new_rule['Actions'])

        # Conditions
        modified_conditions = []
        for condition in new_rule['Conditions']:
            if not self._compare_condition(current_rule['Conditions'], condition):
                modified_conditions.append(condition)

        if modified_conditions:
            modified_rule['Conditions'] = modified_conditions

        return modified_rule