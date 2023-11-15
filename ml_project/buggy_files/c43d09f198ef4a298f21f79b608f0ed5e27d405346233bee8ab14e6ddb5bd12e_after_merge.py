    def _run_check_unless(self, low_data, cmd_opts):
        """
        Check that unless doesn't return 0, and that onlyif returns a 0.
        """
        ret = {"result": False}

        if not isinstance(low_data["unless"], list):
            low_data_unless = [low_data["unless"]]
        else:
            low_data_unless = low_data["unless"]

        def _check_cmd(cmd):
            if cmd == 0 and ret["result"] is False:
                ret.update(
                    {
                        "comment": "unless condition is true",
                        "skip_watch": True,
                        "result": True,
                    }
                )
            elif cmd != 0:
                ret.update({"comment": "unless condition is false", "result": False})

        for entry in low_data_unless:
            if isinstance(entry, six.string_types):
                try:
                    cmd = self.functions["cmd.retcode"](
                        entry, ignore_retcode=True, python_shell=True, **cmd_opts
                    )
                    log.debug("Last command return code: %s", cmd)
                except CommandExecutionError:
                    # Command failed, so notify unless to skip the item
                    cmd = 0
                _check_cmd(cmd)
            elif isinstance(entry, dict):
                if "fun" not in entry:
                    ret["comment"] = "no `fun` argument in unless: {0}".format(entry)
                    log.warning(ret["comment"])
                    return ret

                result = self._run_check_function(entry)
                if self.state_con.get("retcode", 0):
                    _check_cmd(self.state_con["retcode"])
                elif result:
                    ret.update(
                        {
                            "comment": "unless condition is true",
                            "skip_watch": True,
                            "result": True,
                        }
                    )
                else:
                    ret.update(
                        {"comment": "unless condition is false", "result": False}
                    )
            else:
                ret.update(
                    {
                        "comment": "unless condition is false, bad type passed",
                        "result": False,
                    }
                )

        # No reason to stop, return ret
        return ret