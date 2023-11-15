    def get_cookie(self):
        if not os.path.isfile(COOKIE_PATH):
            user = self.set_cookie()
        else:
            with open(COOKIE_PATH, "r") as fh:
                try:
                    user = yaml.safe_load(fh)
                    if user is None:
                        user = self.set_cookie()
                except yaml.reader.ReaderError:
                    user = self.set_cookie()
        return user