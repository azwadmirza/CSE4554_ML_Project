    def get_object_permissions(self, object_id, permissions=None):
        perms = self.get_objects_permissions([object_id], permissions)
        return perms[0] if perms else {}