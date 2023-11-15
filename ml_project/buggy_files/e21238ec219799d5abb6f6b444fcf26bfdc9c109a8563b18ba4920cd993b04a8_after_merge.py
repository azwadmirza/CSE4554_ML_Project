    def _get_json_data(self, url, what, **kwargs):
        # Get the JSON data
        r = self._get_url_data(url, what, **kwargs)

        # Parse the JSON data
        try:
            json_data = json.loads(to_native(r.read()))
        except Exception:
            e = get_exception()
            self.module.fail_json(
                msg="Cannot parse %s JSON data." % what,
                details=to_native(e))

        return json_data