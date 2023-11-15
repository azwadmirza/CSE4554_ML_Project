    def set_cookie(self):
        cookie_dir = os.path.dirname(COOKIE_PATH)
        user = {"id": str(uuid.uuid4())}

        dbt.clients.system.make_directory(cookie_dir)

        with open(COOKIE_PATH, "w") as fh:
            yaml.dump(user, fh)

        return user