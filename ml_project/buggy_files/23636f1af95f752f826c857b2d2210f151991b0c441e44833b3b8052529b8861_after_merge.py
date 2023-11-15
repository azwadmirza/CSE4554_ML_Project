    def set_cookie(self):
        user = {"id": str(uuid.uuid4())}

        dbt.clients.system.make_directory(self.cookie_dir)

        with open(self.cookie_path, "w") as fh:
            yaml.dump(user, fh)

        return user