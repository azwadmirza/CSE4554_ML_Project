    def _process_resource(self, resource):
        lock_name = self._get_lock_name(resource)
        lock_notes = self._get_lock_notes(resource)

        if is_resource_group(resource):
            self.client.management_locks.create_or_update_at_resource_group_level(
                resource['name'],
                lock_name,
                ManagementLockObject(level=self.lock_type, notes=lock_notes)
            )
        else:
            self.client.management_locks.create_or_update_by_scope(
                resource['id'],
                lock_name,
                ManagementLockObject(level=self.lock_type, notes=lock_notes)
            )