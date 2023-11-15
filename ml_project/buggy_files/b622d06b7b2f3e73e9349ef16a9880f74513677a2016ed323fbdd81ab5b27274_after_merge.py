    def get_object_permissions(self, object_id, permissions=None):
        return self.get_objects_permissions([object_id], permissions)[0]