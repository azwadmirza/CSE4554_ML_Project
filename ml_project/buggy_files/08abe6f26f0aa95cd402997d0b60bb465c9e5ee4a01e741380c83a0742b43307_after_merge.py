    def _TransferRequestUploads(self, msg, user, conn, addr):

        # Is user alllowed to download?
        checkuser, reason = self.eventprocessor.CheckUser(user, addr)
        if not checkuser:
            return slskmessages.TransferResponse(conn, 0, reason=reason, req=msg.req)

        # Do we actually share that file with the world?
        realpath = self.eventprocessor.shares.virtual2real(msg.file)
        if not self.fileIsShared(user, msg.file, realpath):
            return slskmessages.TransferResponse(conn, 0, reason="File not shared", req=msg.req)

        # Is that file already in the queue?
        if self.fileIsUploadQueued(user, msg.file):
            return slskmessages.TransferResponse(conn, 0, reason="Queued", req=msg.req)

        # Has user hit queue limit?
        friend = user in [i[0] for i in self.eventprocessor.userlist.userlist]
        if friend and self.eventprocessor.config.sections["transfers"]["friendsnolimits"]:
            limits = False
        else:
            limits = True

        if limits and self.queueLimitReached(user):
            uploadslimit = self.eventprocessor.config.sections["transfers"]["queuelimit"]
            return slskmessages.TransferResponse(conn, 0, reason="User limit of %i megabytes exceeded" % (uploadslimit), req=msg.req)

        if limits and self.fileLimitReached(user):
            filelimit = self.eventprocessor.config.sections["transfers"]["filelimit"]
            limitmsg = "User limit of %i files exceeded" % (filelimit)
            return slskmessages.TransferResponse(conn, 0, reason=limitmsg, req=msg.req)

        # All checks passed, user can queue file!
        self.eventprocessor.frame.pluginhandler.UploadQueuedNotification(user, msg.file, realpath)

        # Is user already downloading/negotiating a download?
        if not self.allowNewUploads() or user in self.getTransferringUsers():

            response = slskmessages.TransferResponse(conn, 0, reason="Queued", req=msg.req)
            newupload = Transfer(
                user=user, filename=msg.file, realfilename=realpath,
                path=os.path.dirname(realpath), status="Queued",
                timequeued=time.time(), size=self.getFileSize(realpath),
                place=len(self.uploads)
            )
            self._appendUpload(user, msg.file, newupload)
            self.uploadspanel.update(newupload)
            self.addQueued(user, realpath)
            return response

        # All checks passed, starting a new upload.
        size = self.getFileSize(realpath)
        response = slskmessages.TransferResponse(conn, 1, req=msg.req, filesize=size)

        transfertimeout = TransferTimeout(msg.req, self.eventprocessor.frame.callback)
        transferobj = Transfer(
            user=user, realfilename=realpath, filename=realpath,
            path=os.path.dirname(realpath), status="Waiting for upload",
            req=msg.req, size=size, place=len(self.uploads)
        )

        self._appendUpload(user, msg.file, transferobj)
        transferobj.transfertimer = threading.Timer(30.0, transfertimeout.timeout)
        transferobj.transfertimer.setDaemon(True)
        transferobj.transfertimer.start()
        self.uploadspanel.update(transferobj)
        return response