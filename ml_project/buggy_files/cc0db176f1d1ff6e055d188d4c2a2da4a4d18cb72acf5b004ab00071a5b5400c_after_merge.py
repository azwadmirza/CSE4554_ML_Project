    def call(self, low, chunks=None, running=None, retries=1):
        """
        Call a state directly with the low data structure, verify data
        before processing.
        """
        utc_start_time = datetime.datetime.utcnow()
        local_start_time = utc_start_time - (
            datetime.datetime.utcnow() - datetime.datetime.now()
        )
        log.info(
            "Running state [%s] at time %s",
            low["name"].strip()
            if isinstance(low["name"], six.string_types)
            else low["name"],
            local_start_time.time().isoformat(),
        )
        errors = self.verify_data(low)
        if errors:
            ret = {
                "result": False,
                "name": low["name"],
                "changes": {},
                "comment": "",
            }
            for err in errors:
                ret["comment"] += "{0}\n".format(err)
            ret["__run_num__"] = self.__run_num
            self.__run_num += 1
            format_log(ret)
            self.check_refresh(low, ret)
            return ret
        else:
            ret = {"result": False, "name": low["name"], "changes": {}}

        self.state_con["runas"] = low.get("runas", None)

        if low["state"] == "cmd" and "password" in low:
            self.state_con["runas_password"] = low["password"]
        else:
            self.state_con["runas_password"] = low.get("runas_password", None)

        if not low.get("__prereq__"):
            log.info(
                "Executing state %s.%s for [%s]",
                low["state"],
                low["fun"],
                low["name"].strip()
                if isinstance(low["name"], six.string_types)
                else low["name"],
            )

        if "provider" in low:
            self.load_modules(low)

        state_func_name = "{0[state]}.{0[fun]}".format(low)
        cdata = salt.utils.args.format_call(
            self.states[state_func_name],
            low,
            initial_ret={"full": state_func_name},
            expected_extra_kws=STATE_INTERNAL_KEYWORDS,
        )
        inject_globals = {
            # Pass a copy of the running dictionary, the low state chunks and
            # the current state dictionaries.
            # We pass deep copies here because we don't want any misbehaving
            # state module to change these at runtime.
            "__low__": immutabletypes.freeze(low),
            "__running__": immutabletypes.freeze(running) if running else {},
            "__instance_id__": self.instance_id,
            "__lowstate__": immutabletypes.freeze(chunks) if chunks else {},
        }

        if "__env__" in low:
            inject_globals["__env__"] = six.text_type(low["__env__"])

        if self.inject_globals:
            inject_globals.update(self.inject_globals)

        if low.get("__prereq__"):
            test = sys.modules[self.states[cdata["full"]].__module__].__opts__["test"]
            sys.modules[self.states[cdata["full"]].__module__].__opts__["test"] = True
        try:
            # Let's get a reference to the salt environment to use within this
            # state call.
            #
            # If the state function accepts an 'env' keyword argument, it
            # allows the state to be overridden(we look for that in cdata). If
            # that's not found in cdata, we look for what we're being passed in
            # the original data, namely, the special dunder __env__. If that's
            # not found we default to 'base'
            req_list = ("unless", "onlyif", "creates")
            if (
                any(req in low for req in req_list)
                and "{0[state]}.mod_run_check".format(low) not in self.states
            ):
                ret.update(self._run_check(low))

            if not self.opts.get("lock_saltenv", False):
                # NOTE: Overriding the saltenv when lock_saltenv is blocked in
                # salt/modules/state.py, before we ever get here, but this
                # additional check keeps use of the State class outside of the
                # salt/modules/state.py from getting around this setting.
                if "saltenv" in low:
                    inject_globals["__env__"] = six.text_type(low["saltenv"])
                elif isinstance(cdata["kwargs"].get("env", None), six.string_types):
                    # User is using a deprecated env setting which was parsed by
                    # format_call.
                    # We check for a string type since module functions which
                    # allow setting the OS environ also make use of the "env"
                    # keyword argument, which is not a string
                    inject_globals["__env__"] = six.text_type(cdata["kwargs"]["env"])

            if "__env__" not in inject_globals:
                # Let's use the default environment
                inject_globals["__env__"] = "base"

            if "__orchestration_jid__" in low:
                inject_globals["__orchestration_jid__"] = low["__orchestration_jid__"]

            if "result" not in ret or ret["result"] is False:
                self.states.inject_globals = inject_globals
                if self.mocked:
                    ret = mock_ret(cdata)
                else:
                    # Execute the state function
                    if not low.get("__prereq__") and low.get("parallel"):
                        # run the state call in parallel, but only if not in a prereq
                        ret = self.call_parallel(cdata, low)
                    else:
                        self.format_slots(cdata)
                        ret = self.states[cdata["full"]](
                            *cdata["args"], **cdata["kwargs"]
                        )
                self.states.inject_globals = {}
            if (
                "check_cmd" in low
                and "{0[state]}.mod_run_check_cmd".format(low) not in self.states
            ):
                ret.update(self._run_check_cmd(low))
        except Exception as exc:  # pylint: disable=broad-except
            log.debug(
                "An exception occurred in this state: %s",
                exc,
                exc_info_on_loglevel=logging.DEBUG,
            )
            trb = traceback.format_exc()
            # There are a number of possibilities to not have the cdata
            # populated with what we might have expected, so just be smart
            # enough to not raise another KeyError as the name is easily
            # guessable and fallback in all cases to present the real
            # exception to the user
            name = (cdata.get("args") or [None])[0] or cdata["kwargs"].get("name")
            if not name:
                name = low.get("name", low.get("__id__"))

            ret = {
                "result": False,
                "name": name,
                "changes": {},
                "comment": "An exception occurred in this state: {0}".format(trb),
            }
        finally:
            if low.get("__prereq__"):
                sys.modules[self.states[cdata["full"]].__module__].__opts__[
                    "test"
                ] = test

            self.state_con.pop("runas", None)
            self.state_con.pop("runas_password", None)

        if not isinstance(ret, dict):
            return ret

        # If format_call got any warnings, let's show them to the user
        if "warnings" in cdata:
            ret.setdefault("warnings", []).extend(cdata["warnings"])

        if "provider" in low:
            self.load_modules()

        if low.get("__prereq__"):
            low["__prereq__"] = False
            return ret

        ret["__sls__"] = low.get("__sls__")
        ret["__run_num__"] = self.__run_num
        self.__run_num += 1
        format_log(ret)
        self.check_refresh(low, ret)
        utc_finish_time = datetime.datetime.utcnow()
        timezone_delta = datetime.datetime.utcnow() - datetime.datetime.now()
        local_finish_time = utc_finish_time - timezone_delta
        local_start_time = utc_start_time - timezone_delta
        ret["start_time"] = local_start_time.time().isoformat()
        delta = utc_finish_time - utc_start_time
        # duration in milliseconds.microseconds
        duration = (delta.seconds * 1000000 + delta.microseconds) / 1000.0
        ret["duration"] = duration
        ret["__id__"] = low["__id__"]
        log.info(
            "Completed state [%s] at time %s (duration_in_ms=%s)",
            low["name"].strip()
            if isinstance(low["name"], six.string_types)
            else low["name"],
            local_finish_time.time().isoformat(),
            duration,
        )
        if "retry" in low:
            low["retry"] = self.verify_retry_data(low["retry"])
            if not sys.modules[self.states[cdata["full"]].__module__].__opts__["test"]:
                if low["retry"]["until"] != ret["result"]:
                    if low["retry"]["attempts"] > retries:
                        interval = low["retry"]["interval"]
                        if low["retry"]["splay"] != 0:
                            interval = interval + random.randint(
                                0, low["retry"]["splay"]
                            )
                        log.info(
                            "State result does not match retry until value, "
                            "state will be re-run in %s seconds",
                            interval,
                        )
                        self.functions["test.sleep"](interval)
                        retry_ret = self.call(low, chunks, running, retries=retries + 1)
                        orig_ret = ret
                        ret = retry_ret
                        ret["comment"] = "\n".join(
                            [
                                (
                                    'Attempt {0}: Returned a result of "{1}", '
                                    'with the following comment: "{2}"'.format(
                                        retries, orig_ret["result"], orig_ret["comment"]
                                    )
                                ),
                                "" if not ret["comment"] else ret["comment"],
                            ]
                        )
                        ret["duration"] = (
                            ret["duration"] + orig_ret["duration"] + (interval * 1000)
                        )
                        if retries == 1:
                            ret["start_time"] = orig_ret["start_time"]
            else:
                ret["comment"] = "  ".join(
                    [
                        "" if not ret["comment"] else six.text_type(ret["comment"]),
                        (
                            "The state would be retried every {1} seconds "
                            "(with a splay of up to {3} seconds) "
                            "a maximum of {0} times or until a result of {2} "
                            "is returned"
                        ).format(
                            low["retry"]["attempts"],
                            low["retry"]["interval"],
                            low["retry"]["until"],
                            low["retry"]["splay"],
                        ),
                    ]
                )
        return ret