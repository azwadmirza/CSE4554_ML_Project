    def get_config(self, key=None, default=None, role="admin",
                   return_bool=False):
        """
        :param key: A key to retrieve
        :type key: string
        :param default: The default value, if it does not exist in the database
        :param role: The role which wants to retrieve the system config. Can be
            "admin" or "public". If "public", only values with type="public"
            are returned.
        :type role: string
        :param return_bool: If the a boolean value should be returned. Returns
            True if value is "True", "true", 1, "1", True...
        :return: If key is None, then a dictionary is returned. If a certain key
            is given a string/bool is returned.
        """
        default_true_keys = [SYSCONF.PREPENDPIN, SYSCONF.SPLITATSIGN,
                             SYSCONF.INCFAILCOUNTER, SYSCONF.RETURNSAML]

        r_config = {}

        # reduce the dictionary to only public keys!
        reduced_config = {}
        for ckey, cvalue in self.config.iteritems():
            if role == "admin" or cvalue.get("Type") == "public":
                reduced_config[ckey] = self.config[ckey]
        if not reduced_config and role=="admin":
            reduced_config = self.config

        for ckey, cvalue in reduced_config.iteritems():
            if cvalue.get("Type") == "password":
                # decrypt the password
                r_config[ckey] = decryptPassword(cvalue.get("Value"))
            else:
                r_config[ckey] = cvalue.get("Value")

        for t_key in default_true_keys:
            if t_key not in r_config:
                r_config[t_key] = "True"

        if key:
            # We only return a single key
            r_config = r_config.get(key, default)

        if return_bool:
            if isinstance(r_config, bool):
                pass
            if isinstance(r_config, int):
                r_config = r_config > 0
            if isinstance(r_config, basestring):
                r_config = is_true(r_config.lower())

        return r_config