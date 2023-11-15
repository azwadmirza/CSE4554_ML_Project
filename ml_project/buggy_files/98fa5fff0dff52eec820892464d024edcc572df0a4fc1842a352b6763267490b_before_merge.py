    def _Refresh(self, ds=None):
        TorrentDetails._Refresh(self, ds)

        self.refresh_counter += 1
        if self.refresh_counter % 5 == 0:
            self.speedPanel.AppendData(0, self.torrent.ds.get_current_speed(DOWNLOAD) / 1024 if self.torrent.ds else 0)
            self.speedPanel.AppendData(1, self.torrent.ds.get_current_speed(UPLOAD) / 1024 if self.torrent.ds else 0)

        # register callback for peerlist update
        self.peerList.Freeze()

        ds = self.torrent.ds
        index = 0
        if ds:
            peers = ds.get_peerlist()

            def downsort(a, b):
                if a.get('downrate', 0) != b.get('downrate', 0):
                    return a.get('downrate', 0) - b.get('downrate', 0)
                return a.get('uprate', 0) - b.get('uprate', 0)
            peers.sort(downsort, reverse=True)

            for peer_dict in peers:
                peer_name = peer_dict['ip'] + ':%d' % peer_dict['port']
                image_index = self.country_to_index.get(peer_dict.get('country', '00').lower(), -1)
                # If this is a hidden services circuit, show a different icon
                tc = self.utility.session.lm.tunnel_community
                if tc and peer_dict['port'] == CIRCUIT_ID_PORT:
                    cid = tc.ip_to_circuit_id(peer_dict['ip'])
                    if cid in tc.circuits and tc.circuits[cid].ctype in [CIRCUIT_TYPE_RENDEZVOUS, CIRCUIT_TYPE_RP]:
                        image_index = self.country_to_index['hidden_services']
                        peer_name = 'Darknet circuit ID %d' % cid

                connection_type = peer_dict.get('connection_type', 0)
                if connection_type == 1:
                    peer_name += ' [WebSeed]'
                elif connection_type == 2:
                    peer_name += ' [HTTP Seed]'
                elif connection_type == 3:
                    peer_name += ' [uTP]'

                if index < self.peerList.GetItemCount():
                    self.peerList.SetStringItem(index, 0, peer_name)
                else:
                    self.peerList.InsertStringItem(index, peer_name)

                if image_index != -1:
                    self.peerList.SetItemColumnImage(index, 0, image_index)

                self.peerList.SetStringItem(index, 1, '%d%%' % (peer_dict.get('completed', 0) * 100.0))

                traffic = ""
                traffic += speed_format(peer_dict.get('downrate', 0)) + u"\u2193 "
                traffic += speed_format(peer_dict.get('uprate', 0)) + u"\u2191"
                self.peerList.SetStringItem(index, 2, traffic.strip())

                state = ""
                if peer_dict.get('optimistic'):
                    state += "O,"
                if peer_dict.get('uinterested'):
                    state += "UI,"
                if peer_dict.get('uchoked'):
                    state += "UC,"
                if peer_dict.get('uhasqueries'):
                    state += "UQ,"
                if not peer_dict.get('uflushed'):
                    state += "UBL,"
                if peer_dict.get('ueligable'):
                    state += "UE,"
                if peer_dict.get('dinterested'):
                    state += "DI,"
                if peer_dict.get('dchoked'):
                    state += "DC,"
                if peer_dict.get('snubbed'):
                    state += "S,"
                state += peer_dict.get('direction', '')
                self.peerList.SetStringItem(index, 3, state)

                if 'extended_version' in peer_dict:
                    try:
                        self.peerList.SetStringItem(index, 4, peer_dict['extended_version'].decode('ascii'))
                    except:
                        try:
                            self.peerList.SetStringItem(
                                index, 4, peer_dict['extended_version'].decode('utf-8', 'ignore'))
                        except:
                            self._logger.error("Could not format peer client version")
                else:
                    self.peerList.SetStringItem(index, 4, '')

                index += 1

            if self.availability:
                self.availability.SetLabel("%.2f" % ds.get_availability())
                self.pieces.SetLabel("total %d, have %d" % ds.get_pieces_total_complete())

                self.availability_vSizer.Layout()

            dsprogress = ds.get_progress()
            # Niels: 28-08-2012 rounding to prevent updating too many times
            dsprogress = long(dsprogress * 1000) / 1000.0
            if self.old_progress != dsprogress and self.filesList.GetItemCount() > 0:
                completion = {}

                useSimple = self.filesList.GetItemCount() > 100
                selected_files = ds.get_download().get_selected_files()
                if useSimple:
                    if selected_files:
                        for i in range(self.filesList.GetItemCount()):
                            file = self.filesList.GetItem(i, 0).GetText()
                            if file in selected_files:
                                completion[file] = dsprogress
                    else:
                        for i in range(self.filesList.GetItemCount()):
                            completion[self.filesList.GetItem(i, 0).GetText()] = dsprogress
                else:
                    for file, progress in ds.get_files_completion():
                        completion[file] = progress

                for i in range(self.filesList.GetItemCount()):
                    listfile = self.filesList.GetItem(i, 0).GetText()

                    if listfile in selected_files or not selected_files:
                        self.filesList.SetStringItem(i, 2, 'Included')
                    else:
                        self.filesList.SetStringItem(i, 2, 'Excluded')

                    progress = completion.get(listfile, None)
                    if isinstance(progress, float) or isinstance(progress, int):
                        self.filesList.SetStringItem(i, 3, "%.2f%%" % (progress * 100))

                self.old_progress = dsprogress

        if index == 0:
            self.peerList.DeleteAllItems()
        else:
            while index < self.peerList.GetItemCount():
                self.peerList.DeleteItem(index)
                index += 1

        self.peerList.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.peerList.SetColumnWidth(2, wx.LIST_AUTOSIZE)
        self.peerList.SetColumnWidth(3, wx.LIST_AUTOSIZE)
        self.peerList.SetColumnWidth(4, wx.LIST_AUTOSIZE)
        self.peerList._doResize()
        self.peerList.Thaw()

        # Tracker status
        ds = self.torrent.ds if self.torrent else None
        if ds:
            new_tracker_status = ds.get_tracker_status()
            if self.old_tracker_status != new_tracker_status:
                self.trackersList.Freeze()

                # Remove items that aren't in the tracker_status dict
                for i in range(self.trackersList.GetItemCount() - 1, -1, -1):
                    if self.trackersList.GetItem(i, 0).GetText() not in new_tracker_status:
                        self.trackersList.DeleteItem(i)

                # Update list
                items = [self.trackersList.GetItem(i, 0).GetText() for i in range(self.trackersList.GetItemCount())]
                tracker_status_items = [(url.encode('ascii', "ignore"), info) for url, info in ds.get_tracker_status().items()]

                for url, info in sorted(tracker_status_items):
                    num_peers, status = info
                    if url in items:
                        self.trackersList.SetStringItem(items.index(url), 1, status)
                        self.trackersList.SetStringItem(items.index(url), 2, str(num_peers))
                    else:
                        self.trackersList.Append([url, status, num_peers])

                self.trackersList.Thaw()
                self.old_tracker_status = new_tracker_status