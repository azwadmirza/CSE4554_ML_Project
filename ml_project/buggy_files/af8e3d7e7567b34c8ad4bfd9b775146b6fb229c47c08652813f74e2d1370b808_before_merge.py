    def is_locked(self, resource: Hashable) -> bool:
        if resource not in self._locks:
            return False
        else:
            return self._locks[resource].locked()