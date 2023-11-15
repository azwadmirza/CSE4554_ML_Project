    def refresh_channels_home(self):
        """
        This function will be called to get popular channel list in Home
        """
        def do_query():
            """
            querying channels to show at home page. Blocking
            :return: dict_channels, dict_torrents, new_channels_ids
            """
            _, channels = self.guiutility.channelsearch_manager.getPopularChannels(2 * MAX_CHANNEL_SHOW)

            dict_channels = {channel.dispersy_cid: channel for channel in channels}
            dict_torrents = {}
            new_channels_ids = list(set(dict_channels.keys()) -
                                    set(self.channels.keys() if not self.channel_list_ready else []))

            for chan_id in new_channels_ids:
                channel = dict_channels.get(chan_id)
                torrents = self.guiutility.channelsearch_manager.getRecentReceivedTorrentsFromChannel(
                    channel, limit=TORRENT_FETCHED)[2]
                dict_torrents[chan_id] = torrents
            return dict_channels, dict_torrents, new_channels_ids

        def do_gui(delayed_result):
            """
            put those new channels in the GUI
            """
            (dict_channels, dict_torrents, new_channels_ids) = delayed_result.get()
            count = 0

            if self.channel_list_ready:
                # reset it. Not reseting torrent_dict because it dynamically added anyway
                self.channels = {}

            for chn_id in new_channels_ids:
                channel = dict_channels.get(chn_id)
                self.channels[chn_id] = channel
                self.chn_torrents.update(dict_torrents)

            self.chn_sizer.Clear(True)
            self.chn_sizer.Layout()
            self.loading_channel_txt.Show()
            for i in xrange(0, COLUMN_SIZE):
                if wx.MAJOR_VERSION > 2:
                    if self.chn_sizer.IsColGrowable(i):
                        self.chn_sizer.AddGrowableCol(i, 1)
                else:
                    self.chn_sizer.AddGrowableCol(i, 1)

            sortedchannels = sorted(self.channels.values(),
                                    key=lambda z: z.nr_favorites if z else 0, reverse=True)

            max_favourite = sortedchannels[0].nr_favorites if sortedchannels else 0

            for chn_id in [x for x in sortedchannels]:
                d = chn_id.dispersy_cid
                # if we can't find channel details, ignore it, or
                # if no torrent available for that channel
                if not dict_channels.get(d) or not len(self.chn_torrents.get(d)):
                    continue

                if self.session.get_creditmining_enable():
                    self.chn_sizer.Add(
                        self.create_channel_item(self.channel_panel, dict_channels.get(d), self.chn_torrents.get(d),
                                                 max_favourite), 0, wx.ALL | wx.EXPAND)

                self.loading_channel_txt.Hide()

                count += 1
                if count >= MAX_CHANNEL_SHOW:
                    break

            if new_channels_ids:
                self.chn_sizer.Layout()
                self.channel_panel.SetupScrolling()

        # quit refreshing if Tribler quitting
        if GUIUtility.getInstance().utility.abcquitting:
            return

        if self.guiutility.frame.ready and isinstance(self.guiutility.GetSelectedPage(), Home):
            startWorker(do_gui, do_query, retryOnBusy=True, priority=GUI_PRI_DISPERSY)

        repeat = len(self.channels) < MAX_CHANNEL_SHOW
        self.channel_list_ready = not repeat

        # try to update the popular channel once in a while
        self.schedule_refresh_channels_home()