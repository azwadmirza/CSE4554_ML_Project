    def get_param_cached(self, key):
        resolved_key = rospy.names.resolve_name(key)
        try:
            # check for value in the parameter server cache
            return rospy.impl.paramserver.get_param_server_cache().get(resolved_key)
        except KeyError:
            # first access, make call to parameter server
            with self._lock:
                code, msg, value = self.target.subscribeParam(rospy.names.get_caller_id(), rospy.core.get_node_uri(), resolved_key)
            if code != 1: #unwrap value with Python semantics
                raise KeyError(key)
            # set the value in the cache so that it's marked as subscribed
            rospy.impl.paramserver.get_param_server_cache().set(resolved_key, value)
            if isinstance(value, dict) and not value:
                raise KeyError(key)
            return value