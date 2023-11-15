	def _user_for_api_key(self, api_key):
		with self._keys_lock:
			for user_id, data in self._keys.items():
				if filter(lambda x: x.api_key == api_key, data):
					return self._user_manager.findUser(userid=user_id)
		return None