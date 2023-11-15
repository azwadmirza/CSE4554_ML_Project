    def get_opt(self, k, defval=""):
        """
        Returns an option from an Optparse values instance.
        """
        try:
            data = getattr(self.options, k)
        except:
            return defval
        # FIXME: Can this be removed if cli and/or constants ensures it's a
        # list?
        if k == "roles_path":
            if os.pathsep in data:
                data = data.split(os.pathsep)[0]
        return data