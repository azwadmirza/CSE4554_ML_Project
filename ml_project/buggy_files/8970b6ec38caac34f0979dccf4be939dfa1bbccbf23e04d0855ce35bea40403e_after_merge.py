    def QueueUpload(self, msg):
        """ Peer remotely(?) queued a download (upload here) """

        user = None
        for i in self.peerconns:
            if i.conn is msg.conn.conn:
                user = i.username

        if user is None:
            return

        addr = msg.conn.addr[0]
        realpath = self.eventprocessor.shares.virtual2real(msg.file)

        if not self.fileIsUploadQueued(user, msg.file):

            friend = user in [i[0] for i in self.eventprocessor.userlist.userlist]
            if friend and self.eventprocessor.config.sections["transfers"]["friendsnolimits"]:
                limits = 0
            else:
                limits = 1

            checkuser, reason = self.eventprocessor.CheckUser(user, addr)

            if not checkuser:
                self.queue.put(
                    slskmessages.QueueFailed(conn=msg.conn.conn, file=msg.file, reason=reason)
                )

            elif limits and self.queueLimitReached(user):
                uploadslimit = self.eventprocessor.config.sections["transfers"]["queuelimit"]
                limitmsg = "User limit of %i megabytes exceeded" % (uploadslimit)
                self.queue.put(
                    slskmessages.QueueFailed(conn=msg.conn.conn, file=msg.file, reason=limitmsg)
                )

            elif limits and self.fileLimitReached(user):
                filelimit = self.eventprocessor.config.sections["transfers"]["filelimit"]
                limitmsg = "User limit of %i files exceeded" % (filelimit)
                self.queue.put(
                    slskmessages.QueueFailed(conn=msg.conn.conn, file=msg.file, reason=limitmsg)
                )

            elif self.fileIsShared(user, msg.file, realpath):
                newupload = Transfer(
                    user=user, filename=msg.file, realfilename=realpath,
                    path=os.path.dirname(realpath), status="Queued",
                    timequeued=time.time(), size=self.getFileSize(realpath)
                )
                self._appendUpload(user, msg.file, newupload)
                self.uploadspanel.update(newupload)
                self.addQueued(user, msg.file)
                self.eventprocessor.frame.pluginhandler.UploadQueuedNotification(user, msg.file, realpath)

            else:
                self.queue.put(
                    slskmessages.QueueFailed(conn=msg.conn.conn, file=msg.file, reason="File not shared")
                )

        self.eventprocessor.logMessage(_("Queued upload request: User %(user)s, %(msg)s") % {
            'user': user,
            'msg': str(vars(msg))
        }, 5)

        self.checkUploadQueue()