    def touch_member(self, data, ttl=None, permanent=False):
        cluster = self.cluster
        member = cluster and cluster.get_member(self._name, fallback_to_leader=False)
        create_member = not permanent and self.refresh_session()

        if member and (create_member or member.session != self._session):
            self._client.kv.delete(self.member_path)
            create_member = True

        if not create_member and member and deep_compare(data, member.data):
            return True

        try:
            args = {} if permanent else {'acquire': self._session}
            self._client.kv.put(self.member_path, json.dumps(data, separators=(',', ':')), **args)
            if self._register_service:
                self.update_service(not create_member and member and member.data or {}, data)
            return True
        except Exception:
            logger.exception('touch_member')
        return False