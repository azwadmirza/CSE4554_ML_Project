    def assign_group_memberships(self):
        """
        Assigns members to groups
        """
        for group in self['groups']:
            for user in self['users']:
                if group in self['users'][user]['groups']:
                    self['groups'][group]['users'].append(user)