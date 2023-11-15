    def _run_check(self, low_data):
        """
        Check that unless doesn't return 0, and that onlyif returns a 0.
        """
        ret = {"result": False, "comment": []}
        cmd_opts = {}

        if "shell" in self.opts["grains"]:
            cmd_opts["shell"] = self.opts["grains"].get("shell")

        if "onlyif" in low_data:
            _ret = self._run_check_onlyif(low_data, cmd_opts)
            ret["result"] = _ret["result"]
            ret["comment"].append(_ret["comment"])
            if "skip_watch" in _ret:
                ret["skip_watch"] = _ret["skip_watch"]

        if "unless" in low_data:
            _ret = self._run_check_unless(low_data, cmd_opts)
            # If either result is True, the returned result should be True
            ret["result"] = _ret["result"] or ret["result"]
            ret["comment"].append(_ret["comment"])
            if "skip_watch" in _ret:
                # If either result is True, the returned result should be True
                ret["skip_watch"] = _ret["skip_watch"] or ret["skip_watch"]

        return ret