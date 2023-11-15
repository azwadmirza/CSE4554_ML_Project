        def authenticate(self, *args, **kwargs):
            if self.global_params["authentication_type"] == "ldap":
                return super(LDAPBackend, self).authenticate(*args, **kwargs)
            return None