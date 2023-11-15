    def _run_check_onlyif(self, low_data, cmd_opts):
        """
        Check that unless doesn't return 0, and that onlyif returns a 0.
        """
        ret = {"result": False}

        if not isinstance(low_data["onlyif"], list):
            low_data_onlyif = [low_data["onlyif"]]
        else:
            low_data_onlyif = low_data["onlyif"]

        def _check_cmd(cmd):
            if cmd != 0 and ret["result"] is False:
                ret.update(
                    {
                        "comment": "onlyif condition is false",
                        "skip_watch": True,
                        "result": True,
                    }
                )
            elif cmd == 0:
                ret.update({"comment": "onlyif condition is true", "result": False})

        for entry in low_data_onlyif:
            if isinstance(entry, six.string_types):
                cmd = self.functions["cmd.retcode"](
                    entry, ignore_retcode=True, python_shell=True, **cmd_opts
                )
                log.debug("Last command return code: %s", cmd)
                _check_cmd(cmd)
            elif isinstance(entry, dict):
                if "fun" not in entry:
                    ret["comment"] = "no `fun` argument in onlyif: {0}".format(entry)
                    log.warning(ret["comment"])
                    return ret

                result = self._run_check_function(entry)
                if self.state_con.get("retcode", 0):
                    _check_cmd(self.state_con["retcode"])
                elif not result:
                    ret.update(
                        {
                            "comment": "onlyif condition is false",
                            "skip_watch": True,
                            "result": True,
                        }
                    )
                else:
                    ret.update({"comment": "onlyif condition is true", "result": False})

            else:
                ret.update(
                    {
                        "comment": "onlyif execution failed, bad type passed",
                        "result": False,
                    }
                )
        return ret