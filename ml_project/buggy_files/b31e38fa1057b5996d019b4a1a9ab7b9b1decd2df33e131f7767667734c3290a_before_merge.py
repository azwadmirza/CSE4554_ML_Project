    def OnExit(self):
        self.utility.session.notifier.notify(NTFY_CLOSE_TICK, NTFY_CREATE, None, None)

        if self.i2i_server:
            self.i2i_server.stop()

        self._logger.info("main: ONEXIT")
        self.ready = False
        self.done = True

        # write all persistent data to disk
        self.utility.session.notifier.notify(NTFY_CLOSE_TICK, NTFY_INSERT, None, 'Write all persistent data to disk')
        wx.Yield()

        if self.webUI:
            self.webUI.stop()
            self.webUI.delInstance()

        if self.frame:
            self.frame.Destroy()
            self.frame = None

        # Don't checkpoint, interferes with current way of saving Preferences,
        # see Tribler/Main/Dialogs/abcoption.py
        if self.utility:
            # Niels: lets add a max waiting time for this session shutdown.
            session_shutdown_start = time()

            # TODO(emilon): probably more notification callbacks should be remmoved
            # here
            s = self.utility.session
            s.remove_observer(self.sesscb_ntfy_newversion)
            s.remove_observer(self.sesscb_ntfy_corrupt_torrent)
            s.remove_observer(self.sesscb_ntfy_magnet)
            s.remove_observer(self.sesscb_ntfy_torrentfinished)
            s.remove_observer(self.sesscb_ntfy_markingupdates)
            s.remove_observer(self.sesscb_ntfy_moderationupdats)
            s.remove_observer(self.sesscb_ntfy_modificationupdates)
            s.remove_observer(self.sesscb_ntfy_commentupdates)
            s.remove_observer(self.sesscb_ntfy_playlistupdates)
            s.remove_observer(self.sesscb_ntfy_torrentupdates)
            s.remove_observer(self.sesscb_ntfy_myprefupdates)
            s.remove_observer(self.sesscb_ntfy_channelupdates)
            s.remove_observer(self.sesscb_ntfy_channelupdates)
            s.remove_observer(self.sesscb_ntfy_activities)
            s.remove_observer(self.sesscb_ntfy_reachable)

            try:
                self._logger.info("ONEXIT cleaning database")
                self.utility.session.notifier.notify(NTFY_CLOSE_TICK, NTFY_INSERT, None, 'Cleaning database')
                wx.Yield()
                torrent_db = self.utility.session.open_dbhandler(NTFY_TORRENTS)
                torrent_db._db.clean_db(randint(0, 24) == 0, exiting=True)
            except:
                print_exc()

            self.utility.session.notifier.notify(NTFY_CLOSE_TICK, NTFY_INSERT, None, 'Shutdown session')
            wx.Yield()
            self.utility.session.shutdown(hacksessconfcheckpoint=False)

            # Arno, 2012-07-12: Shutdown should be quick
            # Niels, 2013-03-21: However, setting it too low will prevent checkpoints from being written to disk
            waittime = 60
            while not self.utility.session.has_shutdown():
                diff = time() - session_shutdown_start
                if diff > waittime:
                    self._logger.info("main: ONEXIT NOT Waiting for Session to shutdown, took too long")
                    break

                self._logger.info(
                    "ONEXIT Waiting for Session to shutdown, will wait for an additional %d seconds",
                    waittime - diff)
                sleep(3)
            self._logger.info("ONEXIT Session is shutdown")

        self.utility.session.notifier.notify(NTFY_CLOSE_TICK, NTFY_INSERT, None, 'Deleting instances')
        self._logger.debug("ONEXIT deleting instances")

        Session.del_instance()
        GUIDBProducer.delInstance()
        DefaultDownloadStartupConfig.delInstance()
        GuiImageManager.delInstance()

        self.utility.session.notifier.notify(NTFY_CLOSE_TICK, NTFY_INSERT, None, 'Exiting now')

        self.utility.session.notifier.notify(NTFY_CLOSE_TICK, NTFY_DELETE, None, None)

        GUIUtility.delInstance()