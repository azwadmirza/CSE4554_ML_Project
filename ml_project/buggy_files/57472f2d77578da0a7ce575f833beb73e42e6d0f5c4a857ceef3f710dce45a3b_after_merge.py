    def OnOk(self, event):
        max = 1 if self.combineRadio.GetValue() else len(self.selectedPaths)
        if self.to_channel:
            dlg = wx.MessageDialog(self, "This will add %d new .torrents to this Channel.\nDo you want to continue?" %
                                   max, "Are you sure?", style=wx.YES_NO | wx.ICON_QUESTION)
        else:
            dlg = wx.MessageDialog(self, "This will create %d new .torrents.\nDo you want to continue?" %
                                   max, "Are you sure?", style=wx.YES_NO | wx.ICON_QUESTION)

        if dlg.ShowModal() == wx.ID_YES:
            dlg.Destroy()

            params = {}
            params['comment'] = self.commentList.GetValue().encode('utf-8')
            params['created by'] = '%s version: %s' % ('Tribler', version_id)

            trackers = self.trackerList.GetValue()
            trackers = [tracker for tracker in trackers.split(os.linesep) if tracker]

            for tracker in trackers:
                self.trackerHistory.AddFileToHistory(tracker)
            self.trackerHistory.Save(self.config)
            self.config.Flush()

            self.filehistory.Save(self.fileconfig)
            self.fileconfig.Flush()

            if trackers:
                params['announce'] = trackers[0]
                params['announce-list'] = trackers

            if self.webSeed.GetValue():
                params['urllist'] = [self.webSeed.GetValue()]

            params['nodes'] = False
            params['httpseeds'] = False
            params['encoding'] = False

            piece_length_list = [0, 2 ** 22, 2 ** 21, 2 ** 20, 2 ** 19, 2 ** 18, 2 ** 17, 2 ** 16, 2 ** 15]
            if self.pieceChoice.GetSelection() != wx.NOT_FOUND:
                params['piece length'] = piece_length_list[self.pieceChoice.GetSelection()]
            else:
                params['piece length'] = 0

            def do_gui():
                if self.cancelEvent.isSet():
                    self.OnCancel(event)
                else:
                    self.EndModal(wx.ID_OK)

            def create_torrents():
                try:
                    if self.combineRadio.GetValue():
                        params['name'] = self.specifiedName.GetValue()
                        create_torrent_file(self.selectedPaths, params, self._torrentCreated)
                    else:
                        for path in self.selectedPaths:
                            if os.path.isfile(path):
                                create_torrent_file([path], params, self._torrentCreated)
                except:
                    print_exc()

                wx.CallAfter(do_gui)

            def start():
                if self.combineRadio.GetValue():
                    self.progressDlg = wx.ProgressDialog(
                        "Creating new .torrents", "Please wait while Tribler is creating your .torrents.\n"
                        "This could take a while due to creating the required hashes.",
                        maximum=max, parent=self,
                        style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE)
                else:
                    self.progressDlg = wx.ProgressDialog(
                        "Creating new .torrents", "Please wait while Tribler is creating your .torrents.\n"
                        "This could take a while due to creating the required hashes.",
                        maximum=max, parent=self,
                        style=wx.PD_CAN_ABORT | wx.PD_APP_MODAL | wx.PD_ELAPSED_TIME | wx.PD_AUTO_HIDE)
                self.progressDlg.Pulse()
                self.progressDlg.cur = 0

                GUIUtility.getInstance().utility.session.lm.threadpool.call_in_thread(0, create_torrents)

            if params['piece length']:
                total_size = 0
                if self.combineRadio.GetValue():
                    for path in self.selectedPaths:
                        total_size += os.path.getsize(path)
                else:
                    for path in self.selectedPaths:
                        total_size = max(total_size, os.path.getsize(path))

                nrPieces = total_size / params['piece length']
                if nrPieces > 2500:
                    dlg2 = wx.MessageDialog(self, "The selected piecesize will cause a torrent to have %d pieces.\n"
                                            "This is more than the recommended max 2500 pieces.\nDo you want to continue?" %
                                            nrPieces, "Are you sure?", style=wx.YES_NO | wx.ICON_QUESTION)
                    if dlg2.ShowModal() == wx.ID_YES:
                        start()
                    dlg2.Destroy()

                else:
                    start()
            else:
                start()
        else:
            dlg.Destroy()