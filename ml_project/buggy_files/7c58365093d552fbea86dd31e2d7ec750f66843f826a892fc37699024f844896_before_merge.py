    def processSearchRequest(self, searchterm, user, searchid, direct=0):

        if not self.config.sections["searches"]["search_results"]:
            # Don't return _any_ results when this option is disabled
            return

        if searchterm is None:
            return

        if user == self.config.sections["server"]["login"]:
            # We shouldn't send a search response if we initiated the search request
            return

        checkuser, reason = self.np.CheckUser(user, None)
        if not checkuser:
            return

        if reason == "geoip":
            geoip = 1
        else:
            geoip = 0

        maxresults = self.config.sections["searches"]["maxresults"]

        if checkuser == 2:
            wordindex = self.config.sections["transfers"]["bwordindex"]
            fileindex = self.config.sections["transfers"]["bfileindex"]
        else:
            wordindex = self.config.sections["transfers"]["wordindex"]
            fileindex = self.config.sections["transfers"]["fileindex"]

        fifoqueue = self.config.sections["transfers"]["fifoqueue"]

        if maxresults == 0:
            return

        terms = searchterm.translate(self.translatepunctuation).lower().split()
        list = [wordindex[i][:] for i in terms if i in wordindex]

        if len(list) != len(terms) or len(list) == 0:
            return

        min = list[0]

        for i in list[1:]:
            if len(i) < len(min):
                min = i

        list.remove(min)

        for i in min[:]:
            for j in list:
                if i not in j:
                    min.remove(i)
                    break

        results = min[:maxresults]

        if len(results) > 0 and self.np.transfers is not None:

            queuesizes = self.np.transfers.getUploadQueueSizes()
            slotsavail = self.np.transfers.allowNewUploads()

            if len(results) > 0:

                message = slskmessages.FileSearchResult(
                    None,
                    self.config.sections["server"]["login"],
                    geoip, searchid, results, fileindex, slotsavail,
                    self.np.speed, queuesizes, fifoqueue
                )

                self.np.ProcessRequestToPeer(user, message)

                if direct:
                    self.logMessage(
                        _("User %(user)s is directly searching for %(query)s, returning %(num)i results") % {
                            'user': user,
                            'query': searchterm,
                            'num': len(results)
                        }, 2)
                else:
                    self.logMessage(
                        _("User %(user)s is searching for %(query)s, returning %(num)i results") % {
                            'user': user,
                            'query': searchterm,
                            'num': len(results)
                        }, 2)