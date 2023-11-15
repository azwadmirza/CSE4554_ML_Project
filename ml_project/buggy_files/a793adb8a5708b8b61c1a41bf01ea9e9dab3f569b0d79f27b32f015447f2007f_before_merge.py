    def set_permissions(self):
        for permission in self._permissions:
            if permission not in self.permissions:
                cmd = ['clear_permissions', '-p']
                cmd.append(permission['vhost'])
                cmd.append(self.username)
                self._exec(cmd)
        for permission in self.permissions:
            if permission not in self._permissions:
                cmd = ['set_permissions', '-p']
                cmd.append(permission['vhost'])
                cmd.append(self.username)
                cmd.append(permission['configure_priv'])
                cmd.append(permission['write_priv'])
                cmd.append(permission['read_priv'])
                self._exec(cmd)