    def _match_rbac_roles_and_principals(self):
        """
        Matches ARM role assignments to AAD service principals
        """
        try:
            if 'rbac' in self.service_list and 'aad' in self.service_list:
                for subscription in self.services['rbac']['subscriptions']:
                    for assignment in self.services['rbac']['subscriptions'][subscription]['role_assignments'].values():
                        role_id = assignment['role_definition_id'].split('/')[-1]
                        for group in self.services['aad']['groups']:
                            if group == assignment['principal_id']:
                                self.services['aad']['groups'][group]['roles'].append({'subscription_id': subscription,
                                                                                     'role_id': role_id})
                                self.services['rbac']['subscriptions'][subscription]['roles'][role_id]['assignments']['groups'].append(group)
                                self.services['rbac']['subscriptions'][subscription]['roles'][role_id]['assignments_count'] += 1
                        for user in self.services['aad']['users']:
                            if user == assignment['principal_id']:
                                self.services['aad']['users'][user]['roles'].append({'subscription_id': subscription,
                                                                                     'role_id': role_id})
                                self.services['rbac']['subscriptions'][subscription]['roles'][role_id]['assignments']['users'].append(user)
                                self.services['rbac']['subscriptions'][subscription]['roles'][role_id]['assignments_count'] += 1
                        for service_principal in self.services['aad']['service_principals']:
                            if service_principal == assignment['principal_id']:
                                self.services['aad']['service_principals'][service_principal]['roles'].append({'subscription_id': subscription,
                                                                                                               'role_id': role_id})
                                self.services['rbac']['subscriptions'][subscription]['roles'][role_id]['assignments']['service_principals'].append(service_principal)
                                self.services['rbac']['subscriptions'][subscription]['roles'][role_id]['assignments_count'] += 1
        except Exception as e:
            print_exception('Unable to match RBAC roles and principals: {}'.format(e))