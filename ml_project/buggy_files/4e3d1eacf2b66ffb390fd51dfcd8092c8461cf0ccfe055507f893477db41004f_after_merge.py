    def _initialize_attributes(self):
        self._short_url = (
            self._fetch_default("short_url") or self.CONFIG_NOT_SET
        )
        self.check_for_updates = self._config_boolean(
            self._fetch_or_not_set("check_for_updates")
        )
        self.kinds = {
            x: self._fetch("{}_kind".format(x))
            for x in [
                "comment",
                "message",
                "redditor",
                "submission",
                "subreddit",
                "trophy",
            ]
        }

        for attribute in (
            "client_id",
            "client_secret",
            "redirect_uri",
            "refresh_token",
            "password",
            "user_agent",
            "username",
        ):
            setattr(self, attribute, self._fetch_or_not_set(attribute))

        for required_attribute in (
            "oauth_url",
            "ratelimit_seconds",
            "reddit_url",
            "timeout",
        ):
            setattr(self, required_attribute, self._fetch(required_attribute))

        for attribute, conversion in {
            "ratelimit_seconds": int,
            "timeout": int,
        }.items():
            try:
                setattr(self, attribute, conversion(getattr(self, attribute)))
            except ValueError:
                raise ValueError(
                    "An incorrect config type was given for option {}. The "
                    "expected type is {}, but the given value is {}.".format(
                        attribute,
                        conversion.__name__,
                        getattr(self, attribute),
                    )
                )