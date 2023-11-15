    def refresh_sourcelist_data(self, rerun=True):
        """
        delete all the source in the list and adding a new one
        """

        # don't refresh if we are quitting
        if GUIUtility.getInstance().utility.abcquitting:
            return

        for i in xrange(0, self.GetItemCount()):
            item = self.GetItem(i)
            data = item.GetData()

            if isinstance(data, ChannelSource):
                if item.GetText() == "Loading..":
                    item.SetText(data.get_source_text() or "Loading..")
                    self.SetItem(item)

        if rerun and not self.guiutility.utility.session.lm.threadpool.is_pending_task_active(
                str(self) + "_refresh_data_ULC"):
            self.guiutility.utility.session.lm.threadpool.add_task(self.refresh_sourcelist_data, 30,
                                                                   task_name=str(self) + "_refresh_data_ULC")