    def set_permissions(self):
        permissions_to_clear = [permission for permission in self._permissions if permission not in self.permissions]
        permissions_to_add = [permission for permission in self.permissions if permission not in self._permissions]
        for permission in permissions_to_clear:
            cmd = 'clear_permissions -p {vhost} {username}'.format(username=self.username,
                                                                   vhost=permission['vhost'])
            self._exec(cmd.split(' '))
        for permission in permissions_to_add:
            cmd = ('set_permissions -p {vhost} {username} {configure_priv} {write_priv} {read_priv}'
                   .format(username=self.username, **permission))
            self._exec(cmd.split(' '))