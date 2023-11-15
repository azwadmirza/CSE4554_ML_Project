    def get_cli_returns(
        self,
        jid,
        minions,
        timeout=None,
        tgt="*",
        tgt_type="glob",
        verbose=False,
        show_jid=False,
        **kwargs
    ):
        """
        Starts a watcher looking at the return data for a specified JID

        :returns: all of the information for the JID
        """
        if verbose:
            msg = "Executing job with jid {}".format(jid)
            print(msg)
            print("-" * len(msg) + "\n")
        elif show_jid:
            print("jid: {}".format(jid))
        if timeout is None:
            timeout = self.opts["timeout"]
        fret = {}
        # make sure the minions is a set (since we do set operations on it)
        minions = set(minions)

        found = set()
        # start this before the cache lookup-- in case new stuff comes in
        event_iter = self.get_event_iter_returns(jid, minions, timeout=timeout)

        # get the info from the cache
        ret = self.get_cache_returns(jid)
        if ret != {}:
            found.update(set(ret))
            yield ret

        # if you have all the returns, stop
        if len(found.intersection(minions)) >= len(minions):
            raise StopIteration()

        # otherwise, get them from the event system
        for event in event_iter:
            if event != {}:
                found.update(set(event))
                yield event
            if len(found.intersection(minions)) >= len(minions):
                self._clean_up_subscriptions(jid)
                raise StopIteration()