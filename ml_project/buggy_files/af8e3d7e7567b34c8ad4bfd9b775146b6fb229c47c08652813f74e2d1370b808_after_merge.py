    def is_locked(self, resource: TResource) -> bool:
        if resource not in self._locks:
            return False
        else:
            return self._locks[resource].locked()