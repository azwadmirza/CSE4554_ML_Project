        def authenticate(self, username, password):
            if self.global_params["authentication_type"] == "ldap":
                return super(LDAPBackend, self).authenticate(
                    username=username, password=password)
            return None