    def remove(self):
        """
        Removes the specified role from the roles path.
        There is a sanity check to make sure there's a meta/main.yml file at this
        path so the user doesn't blow away random directories.
        """
        if self.metadata:
            try:
                rmtree(self.path)
                return True
            except:
                pass

        return False