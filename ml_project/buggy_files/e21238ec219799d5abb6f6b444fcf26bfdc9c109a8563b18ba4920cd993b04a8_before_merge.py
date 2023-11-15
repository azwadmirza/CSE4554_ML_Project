    def _get_json_data(self, url, what, **kwargs):
        # Get the JSON data
        r = self._get_url_data(url, what, **kwargs)

        # Parse the JSON data
        try:
            json_data = json.load(r)
        except Exception:
            e = get_exception()
            self.module.fail_json(
                msg="Cannot parse %s JSON data." % what,
                details=e.message)

        return json_data