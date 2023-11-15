    def get_iter_returns(
        self,
        jid,
        minions,
        timeout=None,
        tgt="*",
        tgt_type="glob",
        expect_minions=False,
        block=True,
        **kwargs
    ):
        """
        Watch the event system and return job data as it comes in

        :returns: all of the information for the JID
        """
        if not isinstance(minions, set):
            if isinstance(minions, str):
                minions = {minions}
            elif isinstance(minions, (list, tuple)):
                minions = set(list(minions))

        if timeout is None:
            timeout = self.opts["timeout"]
        gather_job_timeout = int(
            kwargs.get("gather_job_timeout", self.opts["gather_job_timeout"])
        )
        start = int(time.time())

        # timeouts per minion, id_ -> timeout time
        minion_timeouts = {}

        found = set()
        missing = set()
        # Check to see if the jid is real, if not return the empty dict
        try:
            if (
                self.returners["{}.get_load".format(self.opts["master_job_cache"])](jid)
                == {}
            ):
                log.warning("jid does not exist")
                yield {}
                # stop the iteration, since the jid is invalid
                raise StopIteration()
        except Exception as exc:  # pylint: disable=broad-except
            log.warning(
                "Returner unavailable: %s", exc, exc_info_on_loglevel=logging.DEBUG
            )
        # Wait for the hosts to check in
        last_time = False
        # iterator for this job's return
        if self.opts["order_masters"]:
            # If we are a MoM, we need to gather expected minions from downstreams masters.
            ret_iter = self.get_returns_no_block(
                "(salt/job|syndic/.*)/{}".format(jid), "regex"
            )
        else:
            ret_iter = self.get_returns_no_block("salt/job/{}".format(jid))
        # iterator for the info of this job
        jinfo_iter = []
        # open event jids that need to be un-subscribed from later
        open_jids = set()
        timeout_at = time.time() + timeout
        gather_syndic_wait = time.time() + self.opts["syndic_wait"]
        # are there still minions running the job out there
        # start as True so that we ping at least once
        minions_running = True
        log.debug(
            "get_iter_returns for jid %s sent to %s will timeout at %s",
            jid,
            minions,
            datetime.fromtimestamp(timeout_at).time(),
        )
        while True:
            # Process events until timeout is reached or all minions have returned
            for raw in ret_iter:
                # if we got None, then there were no events
                if raw is None:
                    break
                if "minions" in raw.get("data", {}):
                    minions.update(raw["data"]["minions"])
                    if "missing" in raw.get("data", {}):
                        missing.update(raw["data"]["missing"])
                    continue
                if "return" not in raw["data"]:
                    continue
                if kwargs.get("raw", False):
                    found.add(raw["data"]["id"])
                    yield raw
                else:
                    found.add(raw["data"]["id"])
                    ret = {raw["data"]["id"]: {"ret": raw["data"]["return"]}}
                    if "out" in raw["data"]:
                        ret[raw["data"]["id"]]["out"] = raw["data"]["out"]
                    if "retcode" in raw["data"]:
                        ret[raw["data"]["id"]]["retcode"] = raw["data"]["retcode"]
                    if "jid" in raw["data"]:
                        ret[raw["data"]["id"]]["jid"] = raw["data"]["jid"]
                    if kwargs.get("_cmd_meta", False):
                        ret[raw["data"]["id"]].update(raw["data"])
                    log.debug("jid %s return from %s", jid, raw["data"]["id"])
                    yield ret

            # if we have all of the returns (and we aren't a syndic), no need for anything fancy
            if (
                len(found.intersection(minions)) >= len(minions)
                and not self.opts["order_masters"]
            ):
                # All minions have returned, break out of the loop
                log.debug("jid %s found all minions %s", jid, found)
                break
            elif (
                len(found.intersection(minions)) >= len(minions)
                and self.opts["order_masters"]
            ):
                if (
                    len(found) >= len(minions)
                    and len(minions) > 0
                    and time.time() > gather_syndic_wait
                ):
                    # There were some minions to find and we found them
                    # However, this does not imply that *all* masters have yet responded with expected minion lists.
                    # Therefore, continue to wait up to the syndic_wait period (calculated in gather_syndic_wait) to see
                    # if additional lower-level masters deliver their lists of expected
                    # minions.
                    break
            # If we get here we may not have gathered the minion list yet. Keep waiting
            # for all lower-level masters to respond with their minion lists

            # let start the timeouts for all remaining minions

            for id_ in minions - found:
                # if we have a new minion in the list, make sure it has a timeout
                if id_ not in minion_timeouts:
                    minion_timeouts[id_] = time.time() + timeout

            # if the jinfo has timed out and some minions are still running the job
            # re-do the ping
            if time.time() > timeout_at and minions_running:
                # since this is a new ping, no one has responded yet
                jinfo = self.gather_job_info(
                    jid, list(minions - found), "list", **kwargs
                )
                minions_running = False
                # if we weren't assigned any jid that means the master thinks
                # we have nothing to send
                if "jid" not in jinfo:
                    jinfo_iter = []
                else:
                    jinfo_iter = self.get_returns_no_block(
                        "salt/job/{}".format(jinfo["jid"])
                    )
                timeout_at = time.time() + gather_job_timeout
                # if you are a syndic, wait a little longer
                if self.opts["order_masters"]:
                    timeout_at += self.opts.get("syndic_wait", 1)

            # check for minions that are running the job still
            for raw in jinfo_iter:
                # if there are no more events, lets stop waiting for the jinfo
                if raw is None:
                    break
                try:
                    if raw["data"]["retcode"] > 0:
                        log.error(
                            "saltutil returning errors on minion %s", raw["data"]["id"]
                        )
                        minions.remove(raw["data"]["id"])
                        break
                except KeyError as exc:
                    # This is a safe pass. We're just using the try/except to
                    # avoid having to deep-check for keys.
                    missing_key = exc.__str__().strip("'\"")
                    if missing_key == "retcode":
                        log.debug("retcode missing from client return")
                    else:
                        log.debug(
                            "Passing on saltutil error. Key '%s' missing "
                            "from client return. This may be an error in "
                            "the client.",
                            missing_key,
                        )
                # Keep track of the jid events to unsubscribe from later
                open_jids.add(jinfo["jid"])

                # TODO: move to a library??
                if "minions" in raw.get("data", {}):
                    minions.update(raw["data"]["minions"])
                    continue
                if "syndic" in raw.get("data", {}):
                    minions.update(raw["syndic"])
                    continue
                if "return" not in raw.get("data", {}):
                    continue

                # if the job isn't running there anymore... don't count
                if raw["data"]["return"] == {}:
                    continue

                # if the minion throws an exception containing the word "return"
                # the master will try to handle the string as a dict in the next
                # step. Check if we have a string, log the issue and continue.
                if isinstance(raw["data"]["return"], str):
                    log.error("unexpected return from minion: %s", raw)
                    continue

                if (
                    "return" in raw["data"]["return"]
                    and raw["data"]["return"]["return"] == {}
                ):
                    continue

                # if we didn't originally target the minion, lets add it to the list
                if raw["data"]["id"] not in minions:
                    minions.add(raw["data"]["id"])
                # update this minion's timeout, as long as the job is still running
                minion_timeouts[raw["data"]["id"]] = time.time() + timeout
                # a minion returned, so we know its running somewhere
                minions_running = True

            # if we have hit gather_job_timeout (after firing the job) AND
            # if we have hit all minion timeouts, lets call it
            now = time.time()
            # if we have finished waiting, and no minions are running the job
            # then we need to see if each minion has timedout
            done = (now > timeout_at) and not minions_running
            if done:
                # if all minions have timeod out
                for id_ in minions - found:
                    if now < minion_timeouts[id_]:
                        done = False
                        break
            if done:
                break

            # don't spin
            if block:
                time.sleep(0.01)
            else:
                yield

        # If there are any remaining open events, clean them up.
        if open_jids:
            for jid in open_jids:
                self.event.unsubscribe(jid)

        if expect_minions:
            for minion in list(minions - found):
                yield {minion: {"failed": True}}

        # Filter out any minions marked as missing for which we received
        # returns (prevents false events sent due to higher-level masters not
        # knowing about lower-level minions).
        missing -= found

        # Report on missing minions
        if missing:
            for minion in missing:
                yield {minion: {"failed": True}}