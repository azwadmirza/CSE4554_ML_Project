    def assign_group_memberships(self):
        """
        Assigns members to groups
        """
        try:
            for group in self['groups']:
                for user in self['users']:
                    if group in self['users'][user]['groups']:
                        self['groups'][group]['users'].append(user)
        except Exception as e:
            print_exception('Unable to assign group memberships: {}'.format(e))