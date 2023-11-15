    def update_for_url(self, url):
        """Update settings customized for the given tab.

        Return:
            A set of settings which actually changed.
        """
        changed_settings = set()
        for values in config.instance:
            if not values.opt.supports_pattern:
                continue

            value = values.get_for_url(url, fallback=False)

            changed = self._update_setting(values.opt.name, value)
            if changed:
                log.config.debug("Changed for {}: {} = {}".format(
                    url.toDisplayString(), values.opt.name, value))
                changed_settings.add(values.opt.name)

        return changed_settings