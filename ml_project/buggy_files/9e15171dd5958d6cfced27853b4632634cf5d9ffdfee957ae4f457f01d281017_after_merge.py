    def _compare_listener(self, current_listener, new_listener):
        """
        Compare two listeners.

        :param current_listener:
        :param new_listener:
        :return:
        """

        modified_listener = {}

        # Port
        if current_listener['Port'] != new_listener['Port']:
            modified_listener['Port'] = new_listener['Port']

        # Protocol
        if current_listener['Protocol'] != new_listener['Protocol']:
            modified_listener['Protocol'] = new_listener['Protocol']

        # If Protocol is HTTPS, check additional attributes
        if current_listener['Protocol'] == 'HTTPS' and new_listener['Protocol'] == 'HTTPS':
            # Cert
            if current_listener['SslPolicy'] != new_listener['SslPolicy']:
                modified_listener['SslPolicy'] = new_listener['SslPolicy']
            if current_listener['Certificates'][0]['CertificateArn'] != new_listener['Certificates'][0]['CertificateArn']:
                modified_listener['Certificates'] = []
                modified_listener['Certificates'].append({})
                modified_listener['Certificates'][0]['CertificateArn'] = new_listener['Certificates'][0]['CertificateArn']
        elif current_listener['Protocol'] != 'HTTPS' and new_listener['Protocol'] == 'HTTPS':
            modified_listener['SslPolicy'] = new_listener['SslPolicy']
            modified_listener['Certificates'] = []
            modified_listener['Certificates'].append({})
            modified_listener['Certificates'][0]['CertificateArn'] = new_listener['Certificates'][0]['CertificateArn']

        # Default action

        # Check proper rule format on current listener
        if len(current_listener['DefaultActions']) > 1:
            for action in current_listener['DefaultActions']:
                if 'Order' not in action:
                    self.module.fail_json(msg="'Order' key not found in actions. "
                                              "installed version of botocore does not support "
                                              "multiple actions, please upgrade botocore to version "
                                              "1.10.30 or higher")

        # If the lengths of the actions are the same, we'll have to verify that the
        # contents of those actions are the same
        if len(current_listener['DefaultActions']) == len(new_listener['DefaultActions']):
            # if actions have just one element, compare the contents and then update if
            # they're different
            if len(current_listener['DefaultActions']) == 1 and len(new_listener['DefaultActions']) == 1:
                if current_listener['DefaultActions'] != new_listener['DefaultActions']:
                    modified_listener['DefaultActions'] = new_listener['DefaultActions']
            # if actions have multiple elements, we'll have to order them first before comparing.
            # multiple actions will have an 'Order' key for this purpose
            else:
                current_actions_sorted = sorted(current_listener['DefaultActions'], key=lambda x: x['Order'])
                new_actions_sorted = sorted(new_listener['DefaultActions'], key=lambda x: x['Order'])

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
                    modified_listener['DefaultActions'] = new_listener['DefaultActions']
        # If the action lengths are different, then replace with the new actions
        else:
            modified_listener['DefaultActions'] = new_listener['DefaultActions']

        if modified_listener:
            return modified_listener
        else:
            return None