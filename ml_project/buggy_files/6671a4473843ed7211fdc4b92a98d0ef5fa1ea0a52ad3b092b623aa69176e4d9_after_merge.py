    def transferFile(self, direction, user, filename, path="", transfer=None, size=None, bitrate=None, length=None, realfilename=None):
        """ Get a single file. path is a local path. if transfer object is
        not None, update it, otherwise create a new one."""
        if transfer is None:
            transfer = Transfer(
                user=user, filename=filename, path=path,
                status="Getting status", size=size, bitrate=bitrate,
                length=length
            )

            if direction == 0:
                self.downloads.append(transfer)
            else:
                self._appendUpload(user, filename, transfer)
        else:
            transfer.status = "Getting status"

        try:
            status = self.users[user].status
        except KeyError:
            status = None

        if not direction and self.eventprocessor.config.sections["transfers"]["enablefilters"]:
            # Only filter downloads, never uploads!
            try:
                downloadregexp = re.compile(self.eventprocessor.config.sections["transfers"]["downloadregexp"], re.I)
                if downloadregexp.search(filename) is not None:
                    self.eventprocessor.logMessage(_("Filtering: %s") % filename, 5)
                    self.AbortTransfer(transfer)
                    # The string to be displayed on the GUI
                    transfer.status = "Filtered"
            except Exception:
                pass

        if status is None:
            if user not in self.eventprocessor.watchedusers:
                self.queue.put(slskmessages.AddUser(user))
            self.queue.put(slskmessages.GetUserStatus(user))

        if transfer.status != "Filtered":
            transfer.req = newId()
            realpath = self.eventprocessor.shares.virtual2real(filename)
            request = slskmessages.TransferRequest(None, direction, transfer.req, filename, self.getFileSize(realpath), realpath)
            self.eventprocessor.ProcessRequestToPeer(user, request)

        if direction == 0:
            self.downloadspanel.update(transfer)
        else:
            self.uploadspanel.update(transfer)