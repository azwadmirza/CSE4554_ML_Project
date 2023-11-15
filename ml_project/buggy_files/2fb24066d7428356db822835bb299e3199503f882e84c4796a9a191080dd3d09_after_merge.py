    def has_permissions_modifications(self):
        def to_permission_tuple(vhost_permission_dict):
            return vhost_permission_dict['vhost'], vhost_permission_dict

        def permission_dict(vhost_permission_list):
            return dict(map(to_permission_tuple, vhost_permission_list))

        return permission_dict(self._permissions) != permission_dict(self.permissions)